# The pipeline
This project uses a modular pipeline approach to process images stored in folders. The pipeline is built to be flexible, reusable, and easy to extend, allowing you to define and run custom sequences of processing steps on individual images or entire directories.

python/
├── data/              # Data folder
├── src/               # Core logic and reusable processing steps
├── scripts/           # Entry point scripts (e.g., run_pipeline.py)
├── .venv/             # Virtual environment (ignored by Git)
├── .env               # Python environment config (sets PYTHONPATH)
└── .vscode/           # Editor settings for VS Code

You can modify the parameters in the steps function in the steps.py file, or you can use lambda function to pass the other parameters ass: 


```
steps = {
    "gray": to_grayscale,
    "blurred": lambda img: apply_blur(img, ksize=7),
    "thresholded": lambda img: threshold_image(img, threshold=150),
}
```

# process_folder()
This function is very important because it applies filtering algorithm of the image and a stablished pipelin and prost processing. 

- steps (dict): is the pipeline that process a image 
- prefilter_fn: this kind of function classify the image base in a criteria, for example by a brightness level. 
- 