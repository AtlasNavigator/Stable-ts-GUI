try:
    import torch
    print("Torch imported successfully")
    print(torch.__version__)
    print("CUDA available:", torch.cuda.is_available())
except OSError as e:
    print(f"OSError during import: {e}")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Other error: {e}")
