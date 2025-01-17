


import os
import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Profile')
    parser.add_argument('log_path', metavar='log_path', type=str,
                        help='log path')
    log_path = parser.parse_args().log_path
    send_logs = os.path.join(log_path, 'send_0')
    recv_logs = os.path.join(log_path, 'recv_0')

    lines_send = open(send_logs).readlines()
    lines_recv = open(recv_logs).readlines()
    print(len(lines_send))
    print(len(lines_recv)) 
    class Packet:
        def __init__(self, seq, send_ts, fromapp_ts, rtpts):
            self.seq = seq
            self.send_ts = int(send_ts)
            self.recv = False
            self.recv_ts = None
            self.fromapp_ts = int(fromapp_ts)
            self.toapp_ts = None
            self.rtpts = rtpts
        def add_recv(self, recv_ts):
            self.recv = True
            self.recv_ts = int(recv_ts)
        def delay_ms(self):
            if self.recv is False:
                return None
            return (self.recv_ts - self.send_ts)//1000
        def send_time(self):
            return self.send_ts
        def recv_time(self):
            if self.recv:
                return self.recv_ts
            return None
        def add_toapp(self, app_ts):
            self.toapp_ts = int(app_ts)
        def __str__(self):
            # try:
            #     send_app_delay = (self.send_ts - self.fromapp_ts) // 1000
            #     recv_app_delay = (self.toapp_ts - self.recv_ts) // 1000
            #     return f'Packet {self.rtpts} {self.seq} {send_app_delay} {recv_app_delay}'
            # except:
            #     return ''
            # return f'Packet {self.rtpts} {self.seq} {self.delay_ms()}'
            return f'Packet {self.seq} fromapp {self.fromapp_ts} send {self.send_ts} recv {self.recv_ts} toapp {self.toapp_ts}'
        

    distribution = {}

    class Frame:
        def __init__(self, framesize, captured_time, encoded_time, md5):
            self.framesize = framesize
            self.captured_time = int(captured_time)
            self.encoded_time = int(encoded_time)
            self.md5 = md5
            self.before_decode = None
            self.decoded_time = None
            self.received = False
            self.assembled_time = None
            self.packet = []
        def encode_delay_ms(self):
            if self.captured_time is None:
                return None
            return (self.encoded_time - self.captured_time)/1000
        def decode_delay_ms(self):
            if self.before_decode is None:
                return None
            return (self.decoded_time - self.before_decode)/1000
        def e2e_delay_ms(self):
            if self.captured_time is None or self.decoded_time is None:
                return None
            return (self.decoded_time - self.captured_time)/1000
        # def addpop(self, poptime):
        #     self.poptime.append(int(poptime))
        # def add_recv(self, recvtime):
        #     self.recvtime.append(int(recvtime))
        def add_packet(self, seq, send_ts):
            self.packet.append(Packet(seq, send_ts,self.encoded_time, self.md5))
        def add_recv_packet(self, seq, recv_ts):
            for p in self.packet:
                if p.seq == seq:
                    p.add_recv(recv_ts)
            
        def frame_pop_time(self):
            # return the max of all packet send time
            if len(self.packet) == 0:
                return None
            return max([int(p.send_ts) for p in self.packet])
            
        def send_delay_ms(self):
            if self.encoded_time is None or self.frame_pop_time() is None:
                return None
            return (self.frame_pop_time() - self.encoded_time)/1000
        def recv_delay_ms(self):
            if self.assembled_time is None or self.frame_pop_time() is None:
                return None
            delay = (self.assembled_time - self.frame_pop_time())/1000
            if delay < 0:
                delay = 0
            return delay
        def before_decode_delay_ms(self):
            if self.before_decode is None or self.assembled_time is None:
                return None
            return (self.before_decode - self.assembled_time)/1000
    
        # def get_frame_construction_delay(self):
        #     if self.assembled_time is None or self.recvtime is None:
        #         return None
        #     return (self.assembled_time - min(self.recvtime))/1000
        # def fisrt_packet_delay(self):
        #     if len(self.recvtime) == 0 or len(self.poptime) == 0:
        #         return None
        #     return (min(self.recvtime) - self.frame_pop_time())/1000
        def print_markable_ts(self):
            print(f'Frame {self.md5} size {self.framesize}: ')
            print(f'Captured: {self.captured_time//1000}')
            print(f'Encoded: {self.encoded_time//1000}')
            print(f'Packet level:')
            for p in self.packet:
                print(f'-- Packet {p.seq} send: {p.send_time()} receive: {p.recv_time()}, delay: {p.delay_ms()}')
            print(f'Assembled: {self.assembled_time//1000}')
            print(f'Before Decode: {self.before_decode//1000}')
            print(f'Decoded: {self.decoded_time//1000}')
            print(f'---------')
        def queueing_before_send(self):
            # first packet send time - encoded time
            if len(self.packet) == 0:
                return None
            min_packet_send_time = min([p.send_time() for p in self.packet])
            return (min_packet_send_time - self.encoded_time)//1000
        def frame_sending_delay(self):
            # last packet send time - first packet send time
            if len(self.packet) == 0:
                return None
            max_packet_send_time = max([p.send_time() for p in self.packet])
            min_packet_send_time = min([p.send_time() for p in self.packet])
            return (max_packet_send_time - min_packet_send_time)//1000
        
        def assemble_delay_ms(self):
            # assembled time - first packet recv time
            if len(self.packet) == 0:
                return None
            min_packet_recv_time = min([p.recv_time() for p in self.packet if p.recv_time() is not None])
            if self.assembled_time is None or min_packet_recv_time is None:
                return None
            return (self.assembled_time - min_packet_recv_time)//1000

        def print_markable_delay(self):
            
            print(f'Frame {self.md5} size {self.framesize}: ')
            # print(f'Captured: {self.captured_time//1000}')
            print(f'Encoding delay: {self.encode_delay_ms()}')
            # print(f'Send: {self.send_delay_ms()}')
            print(f'Queueing Before Send', self.queueing_before_send())
            print(f'Sending Delay', self.frame_sending_delay())
            print(f'Packet level:')
            for p in self.packet:
                print(f'-- Packet {p.seq} send: {(p.send_time() - self.encoded_time)//1000} receive: {p.delay_ms()}')
        
            print(f'Assembled Delay: {self.assemble_delay_ms()}')
            print(f'Queueing Before Decode: {self.before_decode_delay_ms()}')
            print(f'Decode Delay: {self.decode_delay_ms()}')
            print(f'---------')
        def first_packet_delay(self):
            if len(self.packet) == 0:
                return None
            first_packet = self.packet[0]
            return (first_packet.delay_ms())
        def markable_delays(self):
            return {
                'encoding': self.encode_delay_ms(),
                'queueing_before_send': self.queueing_before_send(),
                'sending_delay': self.frame_sending_delay(),
                'first_packet_delay': self.first_packet_delay(),
                'assembled_delay': self.assemble_delay_ms(),
                'before_decode_delay': self.before_decode_delay_ms(),
                'decode_delay': self.decode_delay_ms()
            }
        def print_packet_delays(self):
            print(f'Packet level:')
            for p in self.packet:
                print(f'-- Packet {p.seq} send: {(p.send_time() - self.encoded_time)//1000} receive: {p.delay_ms()}')
        
        def set_assembled_time(self, assembled_time):
            self.assembled_time = int(assembled_time)
            for p in self.packet:
                p.add_toapp(self.assembled_time)
    frames_md5 = {}

    for line in lines_send:
        if 'LOG_SEND' in line:
            elements = line.split()[1:]
            if len(elements) < 6:
                continue
            framesize, captured_time, encoded_time, md5 = elements[2], elements[3], elements[4], elements[5]
            if md5 not in frames_md5:
                frame = Frame(framesize, captured_time, encoded_time, md5)
                frames_md5[md5] = frame
        if 'PacketSend ' in line:
            elements = line.split()[1:]
            md5, seq, send_time  = elements[2], elements[3], elements[4]
            if md5 in frames_md5:
                frame = frames_md5[md5]
                frame.add_packet(seq, send_time)

        
    for line in lines_recv:
        if 'LOG_RECV' in line:
            elements = line.split()[1:]
            if len(elements) < 6:
                continue
            framesize, before_decode, decoded_time, md5 = elements[2], elements[3], elements[4], elements[5]
            if md5 in frames_md5:
                frame = frames_md5[md5]
                frame.before_decode = int(before_decode)
                frame.decoded_time = int(decoded_time)
                frame.received = True
        if 'Assembled ' in line:
            elements = line.split()[1:]
            md5, assembled_time = elements[2], elements[3]
            if md5 in frames_md5:
                frame = frames_md5[md5]
                frame.set_assembled_time(assembled_time)
                # frame.assembled_time = int(assembled_time)
        if 'rtp_video_stream_receiver2.cc:798' in line:
            elements = line.split()[1:]
            md5, seq, recv_time = elements[2], elements[3], elements[4]
            if md5 in frames_md5:
                frame = frames_md5[md5]
                frame.add_recv_packet(seq, recv_time)


    # Frame Construction Delay


    def get_z_score(value, li):
        if len(li) == 0:
            return 0,0,0
        mean = sum(li)/len(li)
        std = (sum([(x-mean)**2 for x in li])/len(li))**0.5
        if std == 0:
            return 0,0,0
        z = abs((value - mean)/std)
        return z,mean,std

    # for md5 in frames_md5:
    #     frame = frames_md5[md5]
    #     if frame.received:
    #         print('--------------------------------')
    #         print(f'Frame {frame.md5} size {frame.framesize}')
    #         if 'e2e' not in distribution:
    #             distribution['e2e'] = []
    #         distribution['e2e'].append(frame.e2e_delay_ms())
    #         z_e2e,mean,std = get_z_score(frame.e2e_delay_ms(), distribution['e2e'])
    #         delays = frame.markable_delays()
    #         if z_e2e > 3:
    #             print(f'"e2e: {frame.e2e_delay_ms():.2f}"')
    #         else:
    #             print(f'e2e: {frame.e2e_delay_ms():.2f}')
                
    #         max_z = 0
    #         max_z_key = ''
    #         for k, v in delays.items():
    #             if k not in distribution:
    #                 distribution[k] = []
    #             distribution[k].append(v)
    #             z,mean,std = get_z_score(v, distribution[k])
    #             if z_e2e > 3:
    #                 if z > max_z:
    #                     max_z = z
    #                     max_z_key = k
    #                 print(f'"{k}: mean {mean:.2f} std {std:.2f}, z {z:.2f}"')
    #         print(f'max_z_key {max_z_key}, max_z {max_z}')
    #         for k, v in delays.items():
    #             if z_e2e > 3 and max_z_key == k:
    #                 print(f'"{k}: {v:.2f}"')
    #             else:
    #                 print(f'{k}: {v:.2f}')
    #         frame.print_packet_delays()

    # Packet Level

    for md5 in frames_md5:
        frame = frames_md5[md5]
        if frame.received:
            print('--------------------------------')
            # print frame level
            print('--------------------------------')
            # print e2e delay
            # print(f'Frame {frame.md5} size {frame.framesize}')
            
            frame.print_markable_delay()
            print(f'e2e: {frame.e2e_delay_ms():.2f}')       