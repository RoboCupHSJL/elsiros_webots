echo "Building fresh messages.pb.cc messages.pb.h"
protobuf\lib\protoc.exe --cpp_out=..\player messages.proto