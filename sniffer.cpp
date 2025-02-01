#include <arpa/inet.h>
#include <cstring>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>
#include <pcap.h>
#include <sstream>
#include <chrono>

using namespace std;

int tot_packets = 0, tot_data = 0, timeout = 10, packets_in_last_10s = 0, min_packets = 15;
std::chrono::steady_clock::time_point capture_start_time, capture_end_time;
std::chrono::steady_clock::time_point last_log_time, last_packet_timestamp, last_check_time;
pcap_dumper_t *pcap_out = nullptr;
pcap_dumper_t *pcap_dumper = nullptr;

void handle_packet(const struct pcap_pkthdr *header, const u_char *packet) {
    tot_packets++;
    tot_data += header->len;

    auto pack_time = std::chrono::steady_clock::now();
    if (tot_packets == 1) {
        capture_start_time = pack_time;
    }
    capture_end_time = pack_time;

    last_packet_timestamp = std::chrono::steady_clock::now();

    if (pcap_out) {
        pcap_dump((u_char *)pcap_out, header, packet);
    }

    auto curtime = std::chrono::steady_clock::now();

    if (std::chrono::duration_cast<std::chrono::seconds>(curtime - last_log_time).count() >= 3) {
        cout << "Number of Captured Packets: " << tot_packets << endl;
        last_log_time = curtime;
    }
}

int main() {
    char errbuf[PCAP_ERRBUF_SIZE];
    const char* interface = "lo0"; 

    pcap_t *capture_handle = pcap_open_live(interface, BUFSIZ, 1, 1000, errbuf);
    if (capture_handle == nullptr) {
        cerr << "Error opening capture interface: " << errbuf << endl;
        return 1;
    }

    string output_filename = "captured.pcap";
    pcap_out = pcap_dump_open(capture_handle, output_filename.c_str());

    cout << "Starting capture on interface: " << interface << endl;
    cout << "Saving packets to: " << output_filename.c_str() << endl;

    last_log_time = std::chrono::steady_clock::now();
    last_packet_timestamp = std::chrono::steady_clock::now();
    last_check_time = std::chrono::steady_clock::now();

    while (true) {
        struct pcap_pkthdr *header;
        const u_char *packet;
        int res = pcap_next_ex(capture_handle, &header, &packet);
        if (res == 1) {
            handle_packet(header, packet);
        }

        auto curtime = std::chrono::steady_clock::now();
        if (std::chrono::duration_cast<std::chrono::seconds>(curtime - last_packet_timestamp).count() >= timeout) {
            cout << "\n No packets in 10 seconds, stopping capture." << endl;
            break;
        }

        if (std::chrono::duration_cast<std::chrono::seconds>(curtime - last_check_time).count() >= 10) {
            int packets_in_last_10_sec = tot_packets - packets_in_last_10s;
            if (packets_in_last_10_sec < min_packets) {
                cout << "\n Not enough packets (" << packets_in_last_10_sec << " packets in the last 10 sec). Stopping capture..." << endl;
                break;
            }
            packets_in_last_10s = tot_packets;
            last_check_time = curtime;
        }
    }

    if (pcap_out) {
        pcap_dump_close(pcap_out);
    }
    pcap_close(capture_handle);

    auto capture_duration = std::chrono::duration_cast<std::chrono::seconds>(capture_end_time - capture_start_time).count();
    double pps = capture_duration > 0 ? (double)tot_packets / capture_duration : 0;
    double mbps = capture_duration > 0 ? ((long long)tot_data * 8) / (capture_duration * 1e6) : 0;

    cout << "Total Packets Captured: " << tot_packets << endl;
    cout << "Total Data Transferred: " << tot_data << " bytes" << endl;
    cout << "Capture Duration: " << capture_duration << " seconds" << endl;
    cout << "Packets per second (PPS): " << pps << endl;
    cout << "Megabits per second (Mbps): " << mbps << " Mbps" << endl;

    return 0;
}
