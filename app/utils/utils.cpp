#include "utils.h"

using namespace std;

void read_dpu_info(int* dpu_num, int* sfm_num){
  uint32_t flags = 0;
  int fd = open("/dev/dpu", O_RDWR);
  auto retval = ioctl(fd, DPUIOC_G_INFO, (void*)(&flags));
  close(fd);
  *sfm_num = SFM_NUM(flags);
  *dpu_num = DPU_NUM(flags);
  bool DEBUG = (getenv("DEBUG_RUN") != nullptr);
  if ( DEBUG ) {
    printf("[INFO] DPU cores: %d; SFM cores: %d\n", *dpu_num, *sfm_num);
    if ( *sfm_num == 0 ) {
      cout << "Warning: no SFM hardware available\n";
    }
  }
}
/* Wrap DPU async interfaces for uprobes */
// __attribute__ ((__noinline__))
// int sync_wait_wrapper(vart::Runner* runner,
//                       const std::vector<vart::TensorBuffer*>& inputsPtr,
//                       const std::vector<vart::TensorBuffer*>& outputsPtr) {
//     auto job_id = runner->execute_async(inputsPtr, outputsPtr);
//     int exit_status = runner->wait(job_id.first, -1);

//     return exit_status;
// }

/* Computing L1- adn L2-norms between hw and sw computations */
void compute_norms (const float* hw_softmax_value, const float* softmax_value, const size_t size){
  double diff_vector[size];
  /* Init */
  double l1_norm = 0.;
  double l2_norm = 0.;
  for ( unsigned int k = 0; k < size; k++ ){
    /* Difference */
    diff_vector[k] = hw_softmax_value[k] - softmax_value[k];
    /* Accumulate */
    l1_norm += abs(diff_vector[k]);
    l2_norm += diff_vector[k] * diff_vector[k];
  }
  /* Square root for L2 */
  l2_norm = sqrt(l2_norm);
  cout << "L1-norm of the difference is " << l1_norm << endl;
  cout << "L2-norm of the difference is " << l2_norm << endl;
}

  /**
 * @brief put image names to a vector
 *
 * @param path - path of the image direcotry
 * @param images - the vector of image name
 *
 * @return none
 */
void ListImages(string const& path, vector<string>& images, unsigned int max_images) {
  images.clear();
  struct dirent* entry;

  /*Check if path is a valid directory path. */
  struct stat s;
  lstat(path.c_str(), &s);
  if (!S_ISDIR(s.st_mode)) {
    fprintf(stderr, "Error: %s is not a valid directory!\n", path.c_str());
    exit(1);
  }

  DIR* dir = opendir(path.c_str());
  if (dir == nullptr) {
    fprintf(stderr, "Error: Open %s path failed.\n", path.c_str());
    exit(1);
  }

  int loaded_images = 0;
  while ((entry = readdir(dir)) != nullptr & loaded_images < max_images) {
    if (entry->d_type == DT_REG || entry->d_type == DT_UNKNOWN) {
      string name = entry->d_name;
      string ext = name.substr(name.find_last_of(".") + 1);
      if ((ext == "JPEG") || (ext == "jpeg") || (ext == "JPG") ||
          (ext == "jpg") || (ext == "PNG") || (ext == "png")) {
        images.push_back(name);
        loaded_images++;
      }
    }
  }

  closedir(dir);
}

/**
 * @brief load labels from file to a vector
 *
 * @param path - path of the labels file
 * @param labels - the vector of labels string
 *
 * @return none
 */
void LoadLabels(string const& path, vector<string>& labels) {
  labels.clear();
  ifstream flabels(path);
  if (flabels.fail()) {
    fprintf(stderr, "Error : Open %s failed.\n", path.c_str());
    exit(1);
  }
  string kind;
  while (getline(flabels, kind)) {
    labels.push_back(kind);
  }

  flabels.close();
}

/**
 * @brief calculate softmax
 *
 * @param data - pointer to input buffer
 * @param size - size of input buffer
 * @param result - calculation result
 *
 * @return none
 */
void CPUCalcSoftmax(const int8_t* data, size_t size, float* result,
                    float scale) {
  assert(data && result);
  double sum = 0.0f;

  for (size_t i = 0; i < size; i++) {
    result[i] = exp((float)data[i] * scale);
    sum += result[i];
  }
  for (size_t i = 0; i < size; i++) {
    result[i] /= sum;
  }
}

/**
 * @brief Get top k results according to its probability
 *
 * @param d - pointer to input data
 * @param size - size of input data
 * @param k - calculation result
 * @param vlabels - vector of labels
 *
 * @return Top-1 label
 */
string TopK(const float* d, int size, int k, vector<string>& vlabels) {
  assert(d && size > 0 && k > 0);
  priority_queue<pair<float, int>> q;
  string ret_val;

  for (auto i = 0; i < size; ++i) {
    q.push(pair<float, int>(d[i], i));
  }

  for (auto i = 0; i < k; ++i) {
    pair<float, int> ki = q.top();
    printf("[INFO] top[%d] prob = %.15f  name = %s\n", i, d[ki.second],
           vlabels[ki.second].c_str());
    if ( k == 0 ) {
      ret_val = vlabels[ki.second].c_str();
    }
    q.pop();
  }
  return ret_val;
}

/**
 * @brief Run Softmax function on CPU and hardware (DPU IP)
 *
 * @param FCResult Array of fixed-point values from quantized fully-connected layer
 * @param sfm_num Number of hw SFM accelerators in the DPU
 * @param num_classes Number of input classes
 * @param output_scale Softmax scale parameter
 * @param image OpenCV image to display
 * @param labels List of data labels
 */
static auto hw_sfm_controller = xir::SfmController::get_instance();
void runSoftmax ( std::shared_ptr<xir::SfmController> hwsoftmax, int sfm_num,
                    const int8_t* FCResult, size_t num_classes, float output_scale,
                    // cv::Mat image, vector<string> labels ) {
                    vector<string> labels ) {

  float cpu_softmax_value [num_classes];
  unsigned int group = 1;

  /* Library implementation */
  // vitis::ai::softmax(&FCResult[i * num_classes], scale, cls, group, softmax_value);

  /* Calculate softmax_value on CPU and display TOP-5 classification results */
  auto start = std::chrono::system_clock::now();
  CPUCalcSoftmax(FCResult, num_classes, cpu_softmax_value, output_scale);
  auto end = std::chrono::system_clock::now();
  std::chrono::duration<double> elapsed_seconds = end - start;
  auto cpu_elapsed = elapsed_seconds.count();
  cout << "CPU Softmax elapsed seconds: " << cpu_elapsed << endl;

  string cpu_top1 = TopK(cpu_softmax_value, num_classes, 5, labels);
  /* Display the impage */
  // bool quiet = (getenv("SHOW_IMAGES") == nullptr);
  // if (!quiet) {
  //   cv::imshow("Classification ", image);
  //   cv::waitKey(2000);
  // }

  /* Running hwSFM anyway with original scale */
  // if (hwsoftmax && hwsoftmax->supported(output_scale, cls, group)) {
  //   hwsoftmax->run(&FCResult[i * num_classes], output_scale, cls, group, softmax_value);
  // }
  if ( sfm_num != 0 && hwsoftmax ) {
    // static auto hw_smfc = xir::SfmController::get_instance();
    float hw_softmax_value [num_classes];

    start = std::chrono::system_clock::now();
    /* This call is synchronous */
    hwsoftmax->run(FCResult,
                  output_scale,
                  num_classes,
                  group,
                  hw_softmax_value);

    end = std::chrono::system_clock::now();
    elapsed_seconds = end - start;
    auto dpu_elapsed = elapsed_seconds.count();

    cout << "DPU Softmax elapsed seconds: " << dpu_elapsed << endl;
    cout << "DPU vs CPU speedup: x" << cpu_elapsed / dpu_elapsed << endl;

    string dpu_top1 = TopK(hw_softmax_value, num_classes, 5, labels);

    /* Computing L1- and L2-norms between hw and sw computations */
    compute_norms(hw_softmax_value, cpu_softmax_value, num_classes);
  }

}

int runCNN(const int thread_index, const int num_threads, const size_t num_images_per_thread,
            vart::Runner *runner, GraphInfo shapes, string baseImagePath,
            vector<string> images_names, vector<string> labels, int sfm_num, bool run_softmax) {

  /* get in/out tensors and dims */
  auto outputTensors = runner->get_output_tensors();
  auto inputTensors = runner->get_input_tensors();
  auto out_dims = outputTensors[0]->get_shape();
  auto in_dims = inputTensors[0]->get_shape();
  assert(in_dims[0] == 1);
  assert(out_dims[0] == 1);

  /* get shape info */
  int outSize = shapes.outTensorList[0].size; // Number of classes
  int inSize = shapes.inTensorList[0].size; // Number of pixels
  int inHeight = shapes.inTensorList[0].height;
  int inWidth = shapes.inTensorList[0].width;

  int graphBatchSize = in_dims[0];
  std::vector<std::unique_ptr<vart::TensorBuffer>> inputs, outputs;

  cv::Mat target_image;
  int8_t *imageInputs = new int8_t[inSize * graphBatchSize];
  #define FC_SIZE (graphBatchSize * outSize)
  int8_t *FCResult = new int8_t[FC_SIZE];
  std::vector<vart::TensorBuffer *> inputsPtr, outputsPtr;
  std::vector<std::shared_ptr<xir::Tensor>> batchTensors;

  /* Loop over images */
  size_t thread_offset = thread_index*num_images_per_thread;
  for (unsigned int n = 0; n < num_images_per_thread; n++) {
    // if ( (n & 0x0000003f) == 0 ) {
    //   printf("[INFO] Thread[%d]: %u/%ld\n", thread_index, n+1, num_images_per_thread);
    // }
    // printf("[INFO] Reading tmp_image from %s\n", baseImagePath + images_names[n + thread_offset]);
    cv::Mat tmp_image = cv::imread(baseImagePath + "/" + images_names[n + thread_offset]);

    /*image pre-process*/
    cv::Mat resized_image = cv::Mat(inHeight, inWidth, CV_8SC3);
    cv::resize(tmp_image, resized_image, cv::Size(inHeight, inWidth), 0, 0);

    /* Mean value for resnet50 specified in Caffe prototxt */
    // auto input_scale = get_input_scale(inputTensors[0]);
    // cout << "WARNING: only resizing is performed in image pre-processing\n";
    // float mean[3] = {104, 107, 123};
    // for (int h = 0; h < inHeight; h++) {
    //   for (int w = 0; w < inWidth; w++) {
    //     for (int c = 0; c < 3; c++) {
    //       // imageInputs[i * inSize + h * inWidth * 3 + w * 3 + c] =
    //       imageInputs[h * inWidth * 3 + w * 3 + c] =
    //           (int8_t)((resized_image.at<cv::Vec3b>(h, w)[c] - mean[c]) * input_scale);
    //     }
    //   }
    // }

    /* in/out tensor refactory for batch inout/output */
    batchTensors.push_back(std::shared_ptr<xir::Tensor>(
        xir::Tensor::create(inputTensors[0]->get_name(), in_dims,
                            xir::DataType{xir::DataType::XINT, 8u})));

    inputs.push_back(std::make_unique<CpuFlatTensorBuffer>(
        imageInputs, batchTensors.back().get()));

    batchTensors.push_back(std::shared_ptr<xir::Tensor>(
        xir::Tensor::create(outputTensors[0]->get_name(), out_dims,
                            xir::DataType{xir::DataType::XINT, 8u})));

    outputs.push_back(std::make_unique<CpuFlatTensorBuffer>(
        FCResult, batchTensors.back().get()));

    /* tensor buffer input/output */
    inputsPtr.clear();
    outputsPtr.clear();
    inputsPtr.push_back(inputs[0].get());
    outputsPtr.push_back(outputs[0].get());

    /* Launch and wait for DPU task */
    auto job_id = runner->execute_async(inputsPtr, outputsPtr);
    auto dpu_exit_status = runner->wait(job_id.first, -1);
    assert(dpu_exit_status == 0);

    /* Compute softmax */
    if ( run_softmax ) {
        cout << "\nImage : " << images_names[n] << endl;
        auto output_scale = get_output_scale(outputTensors[0]);
        // runSoftmax(hw_sfm_controller, sfm_num, FCResult, outSize, output_scale, target_image, labels);
        runSoftmax(hw_sfm_controller, sfm_num, FCResult, outSize, output_scale, labels);
    }

    inputs.clear();
    outputs.clear();
    inputs.shrink_to_fit();
    outputs.shrink_to_fit();
    // vector<std::unique_ptr<vart::TensorBuffer>>().swap( inputs );
    // vector<std::unique_ptr<vart::TensorBuffer>>().swap( outputs );

  }

  /* Clean-up */
  delete[] FCResult;
  delete[] imageInputs;
  // inputsPtr.clear();
  // outputsPtr.clear();
  // batchTensors.clear();
  // inputsPtr.shrink_to_fit();
  // outputsPtr.shrink_to_fit();
  // batchTensors.shrink_to_fit();
  // vector<vart::TensorBuffer *>().swap( inputsPtr );
  // vector<vart::TensorBuffer *>().swap( outputsPtr );
  // vector<std::shared_ptr<xir::Tensor>>().swap( batchTensors );

  return thread_index;
}
