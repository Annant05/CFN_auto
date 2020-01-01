from sys import argv
import json
import copy

# variables passed from ansible using shell command
# required count and pwd of role from ansible

# main/driver vars
# No of ec2 servers to launch
count = int(argv[1])  # or  1
# get the pwd of the ansible playbook.
pwd = str(argv[2])  # or '/home/ubuntu/environment/launch-4servers-v2'

dir_cfnbase = pwd + "/templates/cfnbase"
dir_generated = pwd + "/templates/generated"

# read all the json templates for manipulation and merging
basecfn_json = json.loads(open(dir_cfnbase + "/basecfn.json", 'r').read())
base_sgs_json = json.loads(open(dir_cfnbase + "/base_sgs.json", 'r').read())
ec2_json = json.loads(open(dir_cfnbase + "/ec2.json", 'r').read())
output_ip_json = json.loads(
    open(dir_cfnbase + "/output_ip_template.json", 'r').read())

# create the output file before execution.
generated_cfn_template_json = open(dir_generated + "/generated_cfn.json", 'w')


# some predefined strings -> to avoid case-sensetive mistakes in keys
str_resources = "Resources"
str_properties = "Properties"
str_tags = "Tags"
str_output_fngetatt = "Fn::GetAtt"
str_outputs = "Outputs"
str_values = "Value"
dict_ec2_servername_tag = {"Key": "Name", "Value": ""}


# function defination
def generate_template_from_merged():
    #  notes: use dict.dictionary(dict2) to merge two dictionaries
    basecfn_copy = copy.deepcopy(basecfn_json)
    #  add security groups json to the resources section of base template
    basecfn_copy[str_resources].update(base_sgs_json)

    # add no of servers passes using the count variable through loop
    # for no in range(0,count):
    for i in range(0, count):
        servername = f'server{str(i + 1)}'
        # make a seperate different copy of the dictionaries -> to avoid writing in main dictionary
        server_config_dict = copy.deepcopy(ec2_json)
        appendtag_dict = copy.deepcopy(dict_ec2_servername_tag)
        outputs_dict = copy.deepcopy(output_ip_json)

        #  Adding a name tag for the server respective to count
        appendtag_dict[str_values] = "CFN_" + servername
        server_config_dict[str_properties][str_tags].append(appendtag_dict)

        # Adding an output field to the template with server name in "Fn::GetAtt" for publicip
        outputs_dict[str_values][str_output_fngetatt][0] = servername

        # Adding the server root key to be added in the "Resources" in CFN tempalate
        serverconfig = {servername: server_config_dict}
        # Adding the server root key to be added in the "Outputs" in CFN tempalate
        outputconfig = {f'{servername}IPv4': outputs_dict}

        # Finally appending/updating the server confing to the main base template
        basecfn_copy[str_resources].update(serverconfig)
        basecfn_copy[str_outputs].update(outputconfig)
        # print(basecfn_copy[str_outputs])

    # print(basecfn_copy)
    # write the generated/merged dict to a json file.
    generated_cfn_template_json.write(json.dumps(basecfn_copy))
    # print(ec2_json[str_properties][str_tags])


# call function
generate_template_from_merged()
print("Python script executed succesfully :) ")
