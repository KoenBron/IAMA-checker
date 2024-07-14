# Run this file to convert the clusters from input.txt into the required json format in output.txt
# This method is imperfect when just copying the clusters from the original IAMA document

import json

if __name__ == "__main__":
    with open("input.txt", "r") as input:
        # Track the state of the reader
        cluster_mode = True

        # Use list and dict to structure the data
        subcluster = [] 
        subcluster_dict = {
            "subcluster_name": "",
            "examples": ""
        }

        for line in input:
            line = line.strip()
            if line[0] == '-':
                subcluster_dict["examples"] += line + "<br>"
                cluster_mode = False

            else:
                if not cluster_mode:
                    subcluster.append(subcluster_dict.copy())
                    subcluster_dict = dict.fromkeys(subcluster_dict, "")

                subcluster_dict["subcluster_name"] += line
                cluster_mode = True
                    
                    
        subcluster.append(subcluster_dict.copy())
        json_output = json.dumps(subcluster, indent=4)  
        output =  open("output.txt", "w")
        output.write(json_output)

