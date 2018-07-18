#include <stdio.h>
#include <unistd.h>

int main(int argc, char** argv) {
	int no = 0;
	while (no < 10) {
		sleep(1);
		printf("test %d\n", no);
		fflush(stdout);
		++no;
	}
	return 0;
}
