#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

const char *sets[][25] = {
    {"Excellence is not an event",
     "It's a habit",
     "I am alone",
     "I am nothing",
     "I must be extraordinary",
     "I must Be BETTER",
     NULL},
    {"I am not that good",
     "Most people are just bad",
     "I must not be among the most",
     "Do not settle for mediocrity",
     "Be better",
     NULL},
    {"Every hour I waste,",
     "Someone better is moving past me",
     "I must be the best self I can be",
     NULL},
    {"If I truly wish to achieve something,",
     "I must be willing to change",
     "I must be better",
     NULL},
    {"Motivation will not save me",
     "Even if I don't want to do something",
     "I must do it",
     "The universe likes suffering",
     "Better to like suffering",
     "Than to suffer",
     NULL},
    {"A pig who can't fly is just a pig",
    "Be a flying pig",
    "Be more than ordinary",
     NULL},
    {"No one cares about my excuses",
     "Results are the only proof",
     NULL},
    {"Mediocrity is crowded",
     "Thank god I hate crowds",
     NULL},
    {"I'm not smart",
     "I just punish myself consistently",
     NULL},
    {"Even if I dont want to do it",
     "I must do it",
     "No one except mom and dude cares about my hardship",
     "They only see results.",
     "They need results?",
     "Let's show them how the boss does it",
     NULL},
    {"You are dumber than the average person",
     "To keep up with everyone, you must work harder than them",
     "Remember that people without talent require madness",
     "Be mad",
     NULL},
    {"I can do it",
     "I have already done it once,",
     "NOW, ONCE MORE",
     NULL},
    {"Remember the happiness on mom's face on hearing your results",
     "Retain that smile",
     "She deserves that happiness",
     NULL},
    {"I am a masochist",
     "I must learn to love pain and suffering",
     "It is the only way to survive and grow",
     NULL},
    {"No girls, No women",
     "Down to Gehenna or up to the Throne, He travels the fastest who travels alone",
     NULL}

};

int set_count = 15;

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
    center_print("I must make mom proud");
    sleep(2);
    center_print("Remember her sacrifices");
    sleep(3);
    center_print("I have done it once");
    sleep(2);
    center_print("I must do it again");
    sleep(2);
    center_print("I MUST DO IT BETTER");
    sleep(2);
    center_print("You are just a low achieving failure");
    sleep(2);
    center_print("Don't let a good day make you forget that");
    sleep(2);
    

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
