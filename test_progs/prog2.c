#include <stdio.h>
#include <unistd.h>

int main(int argc, char** argv) {
	int no = 0;
	while (1) {
		sleep(1);
		printf("test %d\n", no);
		fflush(stdout);
		--no;
	}
	return 0;
}
