import json
import argparse
import yaml
import boto3


def create_param(client, param, overwrite):
    try:
        response = client.put_parameter(
            Name=param['name'],
            Value=param['value'],
            Type=param['type'],
            Overwrite=overwrite
        )
        return response
    except Exception as error_msg:
        if type(error_msg).__name__ == 'ParameterAlreadyExists':
            message = '{} parameter already exists, please enable parameter overwrite if you want to update existing parameters'.format(param['name'])
            return json.dumps({'HTTPStatusCode':'200', 'message': message})
        raise Exception("{} - {}".format(param['name'], error_msg))

def delete_param(client, param):
    try:
        response = client.delete_parameter(
            Name=param['name']
        )
        return response
    except Exception as error_msg:
        if type(error_msg).__name__ == 'ParameterNotFound':
            message = '{} parameter not found, is your parameter name correct?'.format(param['name'])
            return json.dumps({'HTTPStatusCode':'200', 'message': message})
        raise Exception("{} - {}".format(param['name'], error_msg))

def main():
    try:

        parser = argparse.ArgumentParser()
        parser.add_argument("action", type=str, choices=['create', 'delete'], help="what action needs to be performed")
        args = parser.parse_args()

        # load yaml configuration
        conf_file = open("params.yaml")
        config = yaml.safe_load(conf_file)
        conf_file.close()

        # Connect to AWS SSM
        client = boto3.client('ssm', region_name=config['aws']['region'])
        # Process parameters
        for param in config["parameters"]:
            if args.action == 'create':
                response = create_param(client, param, config['aws']['overwrite_param'])
                print("{}".format(response))
            elif args.action == 'delete':
                response = delete_param(client, param)
                print("{}".format(response))
            else:
                raise Exception("Unsupported action - Supported actions are create/delete.")

    except Exception as error_msg:
        raise Exception("Error - Something bad happened - {}.".format(error_msg))

# main entry point
if __name__ == "__main__":
    main()