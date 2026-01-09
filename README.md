\# Huffman Encoding and Decoding



\## Overview
This project implements \*\*Huffman Coding\*\*, a greedy algorithm used for

\*\*lossless data compression\*\*. The algorithm assigns variable-length

prefix codes to characters based on their frequencies, reducing the

overall size of the encoded data.



\## Features

\- Calculates frequency of characters from input text

\- Constructs Huffman Tree using a priority queue (min-heap)

\- Generates optimal prefix codes for characters

\- Encodes input text into compressed binary form

\- Decodes compressed data back to the original text

\- Displays compression statistics





\## Technologies Used

\- Python

\- Data Structures: Tree, Heap (Priority Queue)

\- Algorithms: Greedy Algorithm

\- File Handling



\## How It Works

1\. Count character frequencies from the input file

2\. Build the Huffman Tree using a min-heap

3\. Generate binary codes by traversing the tree

4\. Encode the input text using generated codes

5\. Decode the encoded data to verify correctness



\## How to Run

* run it on command line arguments
* python filename.py encode input.txt output.huff
* python filename.py decode output.huff out.txt
* By encode we will generate the compressed bits for the characters and store them in the output.huff file which will be created automatically
* for decoding the output.huff file we will decode it by running the respective command on terminal with out.txt file which will be created.





input:

 	file.txt

output:

 	after run we will get a compressed file

Limitations of these approach are

 we have to give the input file with a min of 5 to 6 paragraphs then only we can compresses the file if we give below that then we will definitely more size of the given file which is a big set back for this approach.

