#ifndef CHANNEL_H
#define CHANNEL_H

#include <stdio.h>
#include <strings.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

struct Message {
    char* data;
    int length;
};

struct Response {
    char* data;
    int length;
    bool success;
};

using servable_function = std::function<Response(Message)>;

class Channel {
    public:
        int port;
        struct sockaddr_in server;
        struct sockaddr_in from;
        int sockfd;
        socklen_t fromlen;
        char buf[1024];
        int n;
        servable_function func;

        Channel(int port, servable_function func): port(port), func(func) {
            sockfd = socket(AF_INET, SOCK_DGRAM, 0);
            if (sockfd < 0)
                error("ERROR opening socket");
            bzero((char *) &server, sizeof(server));
            server.sin_family = AF_INET;
            server.sin_addr.s_addr = INADDR_ANY;
            server.sin_port = htons(port);
            if (bind(sockfd, (struct sockaddr *) &server, sizeof(server)) < 0)
                error("ERROR on binding");
        };

        void start() {
            fromlen = sizeof(struct sockaddr_in);
            while (1) {
                n = recvfrom(sockfd, buf, 1024, 0, (struct sockaddr *)&from, &fromlen);
                if (n < 0) error("recvfrom");

                Message message = {buf, n};
                Response response = func(message);
                if (response.success) {
                    n = sendto(sockfd, response.data, response.length, 0, (struct sockaddr *)&from, fromlen);
                    if (n  < 0) error("sendto");
                }
            }
        };

        void error(const char *msg) {
            perror(msg);
            exit(1);
        }
};

#endif // CHANNEL_H