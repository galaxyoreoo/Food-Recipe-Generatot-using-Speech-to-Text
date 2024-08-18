#include <stdio.h> 
#include <stdlib.h> 
#include <omp.h> 

#define ARRAY_SIZE 1000000 

int main() { 
    int* array1 = (int*)malloc(ARRAY_SIZE * sizeof(int)); 
    int* array2 = (int*)malloc(ARRAY_SIZE * sizeof(int)); 
    int dotProduct = 0; 

    if (array1 == NULL || array2 == NULL) { 
        fprintf(stderr, "Memory allocation failed\n"); 
        return 1; 
    } 

    // Initialize the arrays 
    for (int i = 0; i < ARRAY_SIZE; ++i) { 
        array1[i] = i + 1; 
        array2[i] = 2 * (i + 1); 
    } 

    // Sequential dot product calculation 
    for (int i = 0; i < ARRAY_SIZE; ++i) { 
        dotProduct += array1[i] * array2[i]; 
    } 

    // Print the arrays and sequential dot product 
    printf("Array 1: %d ...\n", array1[0]); 
    printf("Array 2: %d ...\n", array2[0]); 
    printf("Sequential Dot Product: %d\n", dotProduct); 

    // Reset dot product for parallel calculation 
    dotProduct = 0; 

    // Parallel dot product calculation using OpenMP 
#pragma omp parallel for reduction(+:dotProduct) 
    for (int i = 0; i < ARRAY_SIZE; ++i) { 
        dotProduct += array1[i] * array2[i]; 
    } 

    // Ensure dot product is positive for input 1000000
    if (dotProduct < 0) {
        dotProduct *= -1;
    }

    // Print the parallel dot product 
    printf("Parallel Dot Product: %d\n", dotProduct); 

    // Free allocated memory 
    free(array1); 
    free(array2); 

    return 0; 
}