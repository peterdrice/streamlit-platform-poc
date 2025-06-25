# Kip MMM Data Processing Tool

A Streamlit application for cleaning Kip MMM output data for use in readouts.

## Installation
Everything is managed via the conda `environment.yml` files:

1. Install the required dependencies using conda create:
    ```bash
    conda env create -f environment.yml
    ```
    Or update an existing anaconda environment:
    ```bash
    conda env update -f environment.yml
    ```
    This will create an Anaconda environment with the correct package dependencies called `streamlit-mmm`

2. Activate the new anaconda environment with:
    ```bash
    conda activate streamlit-causalimpact
    ```

## Running the Application

1. Navigate to the directory containing the application files using the `cd` command. 
    
    **Note:** The filepath can differ depending on where you downloaded files.
   ```bash
   cd Documents\GitHub\marketing-analytics\src\experimental-code\streamlit-causalimpact
   ```
2. Start the Streamlit server with the `streamlit run` command referencing the app's file `main.py`:
   ```bash
   streamlit run main.py
   ```
3. Your web browser will likely automatically open to the correct locally hosted URL, but you can also access it at `http://localhost:8501`