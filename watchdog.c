#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(void) {                                                                                                                                                                                                                                                                                                                                                                
    const char *script = "/home/stup/PERMANENT_STICKY_TIMER/sticky_timer.py";

    printf("%s\n",script);
    while (1) {
        // Check if the script is already running
        int status = system("pgrep -fx 'Sticky Timer' > /dev/null 2>&1");
        int exit_code = WEXITSTATUS(status);
        printf("%d\n",exit_code);

        if (exit_code != 0) {
            // Not running, so start it
            printf("Sticky Timer not found. Starting...\n");
            pid_t pid = fork();
            if (pid == 0) {
                execlp("python3", "python3", script, (char *)NULL);
                perror("execlp failed");
                exit(1);
            }
        } else {
            // Already running
            // printf("Sticky Timer is running.\n");  // optional debug
        }

        sleep(10);  // check every 1 minute
    }
}
