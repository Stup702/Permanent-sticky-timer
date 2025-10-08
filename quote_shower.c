#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

const char *sets[][25] = {//add more here
    {"Excellence is not an event",
     "It's a habit",
     NULL}
};

int set_count = 1;//if added more, change

void clear_screen()
{
    printf("\033[2J\033[H");
    fflush(stdout);
}

void center_print(const char *msg)
{
    int width = 120;
    int pad = (width - (int)strlen(msg)) / 2;
    if (pad < 0)
        pad = 0;
    for (int i = 0; i < pad; i++)
        putchar(' ');
    printf("%s\n\n", msg);
}

int main(void)
{
    srand((unsigned int)time(NULL));

    clear_screen();
    

    int prev = 1;
    while (1)
    {
        int r = rand() % set_count;
        while (r == prev)
        {
            r = rand() % set_count;
        }
        prev = r;

        const char **lines = sets[r];
        clear_screen();

        for (int i = 0; lines[i] != NULL; i++)
        {
            center_print(lines[i]);
            sleep(2);
        }

        sleep(2);
    }

    return 0;
}
