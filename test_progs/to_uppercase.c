#include <ctype.h>
#include <stdio.h>
#include <unistd.h>


char* buffer = NULL;
size_t bufferSize = 0;
ssize_t readBytes = 0;

int main(int argc, char** argv) {
	do {
	    readBytes = getline(&buffer, &bufferSize, stdin);
        for (int i = 0; i < readBytes; ++i) {
           putchar(toupper(buffer[i]));
        }
		fflush(stdout);
	} while (readBytes > 0);
	return 0;
}
