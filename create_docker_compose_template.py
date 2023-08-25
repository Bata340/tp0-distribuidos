from jinja2 import Environment, FileSystemLoader
import math

if __name__ == "__main__":
    valid = False
    
    while not valid:
        numClients = input("How many clients should be created in the docker compose file?: ")
        try:
            numClients = int(numClients)
            if numClients <= 0:
                print("Invalid number.\n")
                valid = False
            else:
                valid = True
        except Exception as e:
            print("Invalid number.\n")
            valid = False
    environment = Environment(loader=FileSystemLoader("./templates/"))
    template = environment.get_template("docker-compose-dev.txt")
    content = template.render(
        numClients=numClients
    )
    outputFilename = "docker-compose-dev.yaml"
    with open(outputFilename, mode="w", encoding="utf-8") as message:
        message.write(content)
        print(f"Wrote 'docker-compose-dev.yaml' succesfuly with "+str(numClients)+" clients.")

