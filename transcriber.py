import multiprocessing
import os
import sys
import queue
import time

def transcription_worker(file_queue, result_queue, model_name, language, output_format):
    """
    Worker function that runs in a separate process.
    This allows us to terminate it forcefully if needed.
    """
    try:
        import stable_whisper
        result_queue.put(("log", f"Loading model '{model_name}'..."))
        model = stable_whisper.load_model(model_name)
        result_queue.put(("log", "Model loaded."))

        while True:
            try:
                # Get next file from queue (non-blocking with timeout)
                file_info = file_queue.get(timeout=0.5)
                if file_info is None:  # Poison pill to stop
                    break
                
                index, total_files, file_path = file_info
                filename = os.path.basename(file_path)
                result_queue.put(("log", f"Processing {index + 1}/{total_files}: {filename}"))
                
                try:
                    # Progress callback for real-time updates
                    def progress_callback(seek, total_duration):
                        if total_duration > 0:
                            file_progress = seek / total_duration
                            # Calculate overall progress: completed files + current file progress
                            overall_progress = (index + file_progress) / total_files
                            result_queue.put(("file_progress", (overall_progress, index + 1, total_files, file_progress * 100)))
                    
                    # Prepare arguments
                    transcribe_args = {
                        "audio": file_path,
                        "progress_callback": progress_callback
                    }
                    if language and language != "Auto":
                        transcribe_args["language"] = language
                    
                    # Run transcription
                    result = model.transcribe(**transcribe_args)
                    
                    # Save output
                    base_name = os.path.splitext(file_path)[0]
                    output_file = f"{base_name}.{output_format}"
                    
                    if output_format == "vtt":
                        result.to_srt_vtt(output_file, vtt=True)
                    elif output_format == "srt":
                        result.to_srt_vtt(output_file, vtt=False)
                    elif output_format == "txt":
                        result.to_txt(output_file)
                    elif output_format == "json":
                        result.save_as_json(output_file)
                    
                    result_queue.put(("log", f"Saved to {output_file}"))
                    result_queue.put(("progress", (index + 1, total_files)))
                    
                except Exception as e:
                    result_queue.put(("log", f"Error processing {filename}: {str(e)}"))
            
            except queue.Empty:
                # No more files, check if we should continue waiting
                continue
        
        result_queue.put(("done", None))
        
    except Exception as e:
        result_queue.put(("error", f"Critical Error: {str(e)}"))


class TranscriptionManager:
    def __init__(self, update_callback, finish_callback, file_progress_callback=None):
        self.update_callback = update_callback
        self.finish_callback = finish_callback
        self.file_progress_callback = file_progress_callback
        self.is_running = False
        self.process = None
        self.file_queue = None
        self.result_queue = None
        self.poll_job = None
        self.app = None  # Will be set when start is called

    def start(self, files, model_name, language, output_format, app=None):
        if self.is_running:
            return
        
        self.is_running = True
        self.app = app
        
        # Create multiprocessing queues
        self.file_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        
        # Add all files to the queue
        total_files = len(files)
        for index, file_path in enumerate(files):
            self.file_queue.put((index, total_files, file_path))
        
        # Start the worker process
        self.process = multiprocessing.Process(
            target=transcription_worker,
            args=(self.file_queue, self.result_queue, model_name, language, output_format)
        )
        self.process.daemon = True
        self.process.start()
        
        # Start polling for results
        self._poll_results()

    def _poll_results(self):
        """Poll the result queue for updates from the worker process."""
        try:
            while True:
                try:
                    msg_type, msg_data = self.result_queue.get_nowait()
                    
                    if msg_type == "log":
                        self.update_callback(msg_data)
                    elif msg_type == "file_progress":
                        # Real-time progress during file transcription
                        if self.file_progress_callback:
                            self.file_progress_callback(msg_data)
                    elif msg_type == "progress":
                        completed, total = msg_data
                        self.finish_callback(completed, total)
                    elif msg_type == "done":
                        self.update_callback("All tasks finished.")
                        self._cleanup()
                        return
                    elif msg_type == "error":
                        self.update_callback(msg_data)
                        self._cleanup()
                        return
                        
                except queue.Empty:
                    break
            
            # Check if process is still alive
            if self.process and self.process.is_alive():
                # Schedule next poll
                if self.app:
                    self.poll_job = self.app.after(100, self._poll_results)
            else:
                # Process died unexpectedly
                if self.is_running:
                    self.update_callback("Transcription process ended unexpectedly.")
                    self._cleanup()
                    
        except Exception as e:
            self.update_callback(f"Polling error: {str(e)}")
            self._cleanup()

    def stop(self):
        """Forcefully terminate the transcription process."""
        if self.process and self.process.is_alive():
            self.update_callback("Forcefully stopping transcription...")
            self.process.terminate()
            self.process.join(timeout=2)
            
            # If still alive, kill it
            if self.process.is_alive():
                self.process.kill()
                self.process.join(timeout=1)
            
            self.update_callback("Transcription stopped.")
        
        self._cleanup()

    def _cleanup(self):
        """Clean up resources."""
        self.is_running = False
        
        if self.poll_job and self.app:
            try:
                self.app.after_cancel(self.poll_job)
            except:
                pass
            self.poll_job = None
        
        self.process = None
        self.file_queue = None
        self.result_queue = None
