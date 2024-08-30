# isles24-docker-template

This is an example Docker template for submitting to the ISLES'24 challenge.

## Instructions

1. **Clone this repository.**

2. **Download and decompress the [example image](https://drive.switch.ch/index.php/s/HCrdrSC556tWfRK) to be used for testing your algorithm.** The structure of your local repo should look like this:

    ```plaintext
    isles24-docker-template/
    ├── test/
    │   ├── input/
    │   │   ├── images/
    │   │   │   ├── non-contrast-ct/
    │   │   │   │   └── xxx.mha
    │   │   │   ├── cbf-parameter-map/
    │   │   │   │   └── xxx.mha
    │   │   └── acute_stroke_clinical_information.json
    │   └── output/  # This will be created by your script
    └── (... other files ...)
    ```

3. **Update the scripts.**

   3.1 **Update `inference.py` script** by including your algorithmic solution. Note: As the challenge data is heavy, only read the images that your algorithm needs!

   3.2 **Update `requirements.txt`** by including all the packages your algorithm needs. You can specify package versions, e.g.:

    ```plaintext
    SimpleITK
    numpy
    torch==2.4.0
    ```

4. **Test your algorithm** by running `./test_run.sh`. This script should predict the example image, saving the result in `test/output/`.

5. **Export and prepare the container for upload to Grand-Challenge.org.**

   - **Option 1: Save and upload your Docker image to Grand-Challenge.** You can do this by saving the Docker image as a `.tar.gz` file and then uploading it:

     ```sh
     docker save example-algorithm-preliminary-docker-evaluation | gzip -c > example-algorithm-preliminary-docker-evaluation.tar.gz
     ```

   - **Option 2: Link a GitHub repository to Grand-Challenge for building and integration.** Create your own GitHub repository and follow [these instructions](https://grand-challenge.org/documentation/linking-a-github-repository-to-your-algorithm/).

6. **Further information** about preparing Dockers for Grand-Challenge can be found [here](https://grand-challenge.org/documentation/create-your-own-algorithm/).
