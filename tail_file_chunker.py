import os, sys, time
from optparse import OptionParser

def rotate_output_file(output):
    output_size = os.fstat(output.fileno()).st_size
    output.close()
    if output_size == 0:
        try:
                os.unlink(output.name)
        except OSError:
                pass
    else:
        os.rename(output.name, output.name + ".closed")
    output_time = time.time()
    output = open(params.output_file + str(int(output_time)), "w")
    return output, output_time

def open_input_file(filename):
        log = open(filename, "r");
        log_inode = os.fstat(log.fileno()).st_ino
        return log, log_inode


#validate input params
required_params = ['input_file']
parser = OptionParser()
parser.add_option("--input-file", help="path to the input file", metavar="somefile.log")
parser.add_option("--output-file", help="path to the output file", metavar="somefile.log")
parser.add_option("--time", type="int", help="The number of seconds before rolling over to a new output file", metavar=300, default=300)
parser.add_option("--size", type="int", help="The number of megabytes before rolling over to a new output file", metavar=500, default=500)
parser.add_option("--delay", type = "float", help="The number of seconds to wait before checking the log file again", metavar=0.2)
(params, args) = parser.parse_args()
for required in required_params:
        if params.__dict__[required] is None:
                parser.print_help()
                sys.exit(1)


if params.output_file is None:
        params.output_file = params.input_file
elif os.path.isdir(params.output_file):
        params.output_file += "/" + os.path.basename(params.input_file)
output, output_time = rotate_output_file(open(os.devnull))
log, log_inode = open_input_file(params.input_file)


print "starting with the following params", params
while True:
    #read all the lines available
    while True:
        line = log.readline()
        if line == "":
                break
        output.write(line)
    output.flush()

    #Check if the log has rotated
    try:
        if os.stat(params.input_file).st_ino != log_inode:
            log, log_inode = open_input_file(params.input_file)
    except OSError:
        pass #catch the os error incase the file doesnt exist while rotating.

    #check if we need to rotate the output file by time
    if params.time:
        if time.time() - output_time > params.time:
                output, output_time = rotate_output_file(output)

    #check if we need to rotate the output file by size
    if params.size:
        if os.fstat(output.fileno()).st_size > params.size * 1024 ** 2: #param.size is in Mbs
                output, output_time = rotate_output_file(output)

    #delay the next reading of the log file if se
    if params.delay:
        time.sleep(params.delay)
