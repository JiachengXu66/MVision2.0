# VLink

VLink relies on three things: 
- TS compiler for new builds
- config.json

## TS Compiler
To keep language base the same as that of angular TS has been used. However as a nodeJS api it needs to run via JS. 
Therefore NodeNext is used to compile into JS before building the docker container.
Can be done by running npm run build in the directory

## Config
Shown in the "examples" section it should be located in the VLink folder
```json
{
    "allowedIps":["::ffff:XXX.XXX.X.XXX","::ffff:XXX.XXX.XX.XXX"],
    "corsIps":["http://localhost:4200",
                "http://localhost:8080",
                "http://XXX.XXX.XXX.XXX:4200",
                "http://XXX.XXX.0.XXX:4200",
                "http://XXX.XXX.XX.XXX:4200"]
}
```
allowedIps 

Indicates the Ips that do not require an API key to communicate with the service and are loaded at build. It has to be in ipv6-ipv4 converison format as above. 

Will need to hold all docker service ips running on the master server, these need to be constant and therefore setting up a network bridge specifically for the compose services is required (name should match that in docker compose file)

corsIps

Holds the ips of devices that should be allow to access the api via the browser. This needs a more permanent solution but for now this works if you only have a few devices that need to use the frontend.