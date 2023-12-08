#ifndef __UTILS_H__
#define __UTILS_H__

#include <assert.h>
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <unistd.h>

#include <cassert>
#include <cmath>
#include <cstdio>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <queue>
#include <string>
#include <vector>
#include <chrono>
#include <opencv2/opencv.hpp>
#include "xir/sfm_controller.hpp" /* for xir::SfmController in vart-dpu-controller?*/
#include <vart/runner.hpp> /* for namespace vart and runner in libvart-runner */
#include <xir/tensor/tensor.hpp> /* for TensorBuffer */
#include <sys/ioctl.h> /* for ioctl */
#include <fcntl.h>  /* fpr opne() */
// #include <unistd.h>

#include "dpu.h" /* for DPU_NUM and SFM_NUM macros */
#include "common.h" /* for getTensorShape() */
// #include "vitis/softmax.hpp" /* for vitis::ai::softmax() in libvitis_ai_library-math */

using namespace std;

/**
 * @brief Read /dev/dpu info and print of stdout
 * 
 * @param dpu_num reference to int, number of DPU cores
 * @param sfm_num reference to int, number of SFM cores
 */
void read_dpu_info(int* dpu_num, int* sfm_num);

/**
 * @brief Computing L1- adn L2-norms between hw and sw computations 
 * 
 * @param hw_softmax_value Array of DPU-computed softmax values
 * @param softmax_value Array of CPU-computed softmax values
 * @param size length of the arrays
 */
void compute_norms (const float* hw_softmax_value, const float* softmax_value, const size_t size);

/**
 * @brief Put image names to a vector
 * 
 * @param path directory path
 * @param images list of image file names
 * @param max_images maximum number of names to load
 */
void ListImages(string const& path, vector<string>& images, unsigned int max_images);

/**
 * @brief load kinds from file to a vector
 *
 * @param path - path of the kinds file
 * @param kinds - the vector of kinds string
 *
 * @return none
 */
void LoadLabels(string const& path, vector<string>& kinds);

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
                    float scale);

/**
 * @brief Get top k results according to its probability
 *
 * @param d - pointer to input data
 * @param size - size of input data
 * @param k - calculation result
 * @param vkinds - vector of kinds
 *
 * @return none
 */
string TopK(const float* d, int size, int k, vector<string>& vkinds);

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
void runSoftmax ( std::shared_ptr<xir::SfmController> hwsoftmax, int sfm_num, 
                    const int8_t* FCResult, size_t num_classes, float output_scale,
                    // cv::Mat image, vector<string> labels ) ;
                    vector<string> labels ) ;


/**
 * @brief run DPU task and sw/hw softmax
 * 
 * @param runner Reference to a DPU runner 
 * @param shapes GraphInfo object
 * @param baseImagePath images directory
 * @param images_names list of image names
 * @param labels list of classes
 * @param hw_sfm_controller Softmax controller object
 * @return thread_index
 */
int runCNN(const int thread_index, const int num_threads, const size_t num_images_per_thread,
            vart::Runner *runner, GraphInfo shapes, string baseImagePath, 
            vector<string> images_names, vector<string> labels, int sfm_num, bool run_softmax);

#endif /* __UTILS_H__ */