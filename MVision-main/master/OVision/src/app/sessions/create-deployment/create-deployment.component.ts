import { ChangeDetectorRef, Component } from '@angular/core';
import { Router } from '@angular/router';

import { GetMapService } from '../../passive/get-maps.service';
import { GetTargetService } from '../../targets/get-targets.service';
import { CreateDeploymentService } from './create-deployment.service';
import { GetModelService } from '../../models/get-models.service';
import { GetNodesService } from '../../nodes/get-nodes.service';

import { Target, Location, Person, Model, ModelConfig, Node, Device, Deployment } from '../../../shared/models/Entities';

type Map = { [key: string]: string };

@Component({
  selector: 'app-create-deployment',
  templateUrl: './create-deployment.component.html',
  styleUrls: ['./create-deployment.component.sass']
})
export class CreateDeploymentComponent { 

  deploymentName: Deployment['deployment_name'] = '';
  deploymentStart: string = '';
  deploymentEnd:  string = '';

  targetButtonStatus: boolean = false;
  modelButtonStatus: boolean = true;
  nodeButtonStatus: boolean = true;  
  deviceButtonStatus: boolean = true
  submitButtonStatus: boolean = true

  displayOptionsTarget: boolean = true;
  displayOptionsModel: boolean = false;
  displayOptionsNode: boolean = false;
  displayOptionsDevice: boolean = false;
  
  modelName: string = '';
  models: Model[] = [];
  selectedModel: Model | null = null;
  configMap: ModelConfig[] = [];
  modelConfiguration: string = '';
  modelClasses: string[] = [];
  showModelPopup: boolean = false;
  modelInfoClasses: string [] = []

  persons: Person[] = [];
  locations: Location[] = [];
  selectedTarget: Target | null = null;
  selectedPerson: Person | null = null;
  personAge: number = 1;
  selectedLocation: Location | null = null;

  nodes: Node[] = [];
  selectedNode: Node | null = null;

  devices: Device [] = []
  selectedDevice: Device | null = null;

  currentPage: number = 1;
  itemsPerPage: number = 4;
  targetLength:  number = 1;
  modelLength:  number = 1;
  nodeLength:  number = 1;
  deviceLength: number = 8;
  
  classMap: Map | null = null;
  categoryMap: Map | null = null;

  constructor(private cdr: ChangeDetectorRef,
    private router: Router,
    private mapService: GetMapService,
    private createDeployment: CreateDeploymentService,
    private getTargetService: GetTargetService,
    private getModels: GetModelService,
    private getNodes: GetNodesService
    ) { }


  ngOnInit() {
    this.fetchClassMap();
    this.fetchConfigurationMap();
    this.fetchTargetCount();
    this.fetchModelCount()
    this.fetchNodeCount();
    this.fetchTargets();
    this.fetchModel();
    this.fetchNode();
  } 

  //Selection Functions
  updateTargetSelection(target: Person | Location){
    this.selectedTarget = target;
    if (target instanceof Location)
    {
      this.selectedLocation = target;
      this.selectedPerson = null;
    }
    else if (target instanceof Person)
    {
      this.selectedPerson = target;
      this.selectedLocation = null;
      this.personAge = target.getAge(target.dob)
    }
    this.modelButtonStatus = false;
  }

  updateModelSelection(model: Model){
    this.selectedModel = model;
    this.nodeButtonStatus = false;
    this.modelConfiguration = this.mapModelConfiguration(this.selectedModel)
    this.fetchModelClasses(model, this.classMap!, (classNames) => {
      this.modelClasses = classNames;
    });
  }

  updateNodeSelection(node: Node){
    this.selectedNode = node;
    this.deviceButtonStatus = false;
  }

  updateDeviceSelection(device: Device){
    this.selectedDevice = device;
    this.submitButtonStatus = false;
  }

  //Display Functions
  selectTarget(){
    this.displayOptionsNode = false;
    this.displayOptionsDevice = false;
    this.displayOptionsModel = false;

    this.displayOptionsTarget = true;
    this.currentPage=1
    this.fetchTargets();
    this.fetchTargetCount();
  }
  selectModel(){
    this.displayOptionsNode = false;
    this.displayOptionsDevice = false;
    this.displayOptionsTarget = false;
    
    this.displayOptionsModel = true;
    this.currentPage=1
    this.fetchModel();
    this.fetchModelCount();
  }
  selectNode(){
    this.displayOptionsTarget = false;
    this.displayOptionsDevice = false;
    this.displayOptionsModel = false;

    this.displayOptionsNode = true;
    this.currentPage=1
    this.fetchNode()
    this.fetchNodeCount();
  }
  selectDevice(){
    this.displayOptionsTarget = false;
    this.displayOptionsNode = false;
    this.displayOptionsModel = false;

    this.displayOptionsDevice = true;
    this.currentPage=1
    this.fetchDevice(this.selectedNode!['node_id'])
    this.fetchNodeCount();
  }

  checkDate(date: string){
    const parts = date.split('/'); 
    return new Date(parseInt(parts[2]), parseInt(parts[1])-1, parseInt(parts[0])); 
  }

  submitDeployment(){
    if (!this.deploymentName.trim()) {
      console.log('Target Name must not be empty.');
    }
    else{
      const start = this.checkDate(this.deploymentStart);
      const end = this.checkDate(this.deploymentEnd);
      const new_deployment = new Deployment(9999, this.deploymentName, this.selectedTarget!.target_id, "New", this.selectedModel!.model_id, new Date(), start, end, this.selectedNode!.node_id, this.selectedDevice!.device_id);
      this.createDeployment.postDeployment(new_deployment).subscribe({
        next: (response) => console.log(response),
        error: (error) => console.error('Error:', error),}); 
        this.cdr.detectChanges();
        this.changeToView();
      
    }
  }  

  changeToView(){
    this.router.navigate(['/sessions/view'])
  }

  onPageChange(newPage: number) {
    this.currentPage = newPage;
    this.fetchTargets();
    this.fetchModel();
    this.fetchNode();
    if(this.selectedNode)
    {
      this.fetchDevice(this.selectedNode.node_id)
    }
  }

  //Target Functions
  fetchTargetCount(){
    this.mapService.fetchCountMap().subscribe(countMaps => {
      const countMap = countMaps[0]?.get_count_map;
      if (countMap) {
        console.log("Map:"+countMap);
        console.log("Max Length Map:"+countMap['target_count']);
        this.targetLength = countMap['target_count'];
        console.log("Max Length Saved:"+this.targetLength)
        this.cdr.detectChanges();
      } else {
        console.log('Count not retrieved');
      }
    });
  }
  
  fetchTargets() {
    console.log("Fetching Targets");
    try{
      this.getTargetService.getTargetService(this.itemsPerPage, this.currentPage).subscribe({
        next: (data: any[]) => {
          console.log("Fetched data:", data);
  
          this.persons = [];
          this.locations = [];
          data.flatMap(item => item.get_latest_targets).forEach(target => {
          if(target){
              if (target.dob !== null) {
                this.persons.push(new Person(
                  target.target_id,
                  target.target_name,
                  target.alt_name,
                  new Date(target.creation_date),
                  target.status_value,
                  new Date(target.dob),
                  target.role
                ));
              } 
              else {
                this.locations.push(new Location(
                  target.target_id,
                  target.target_name,
                  target.alt_name,
                  new Date(target.creation_date),
                  target.status_value,
                  target.access
                ));
              }
            }
          });
        },
        error: (error) => console.error('Error fetching targets:', error)
      });
    }
    catch{
      console.log("No Targets Found")
    }
  }
  
  //Model Functions
  fetchModelCount(){
    this.mapService.fetchCountMap().subscribe(countMaps => {
      console.log(countMaps);
      console.log(countMaps[0])
      const countMap = countMaps[0]?.get_count_map;
      if (countMap) {
        console.log("Map:"+countMap);
        console.log("Max Length Map:"+countMap['model_count']);
        this.modelLength = countMap['model_count'];
        console.log("Max Length Saved:"+this.modelLength)
        this.cdr.detectChanges();
      } else {
        console.log('Count not retrieved');
      }
    });
  }

  fetchModel() {
    console.log("Fetching Models");
    try{
      this.getModels.getModelService(this.itemsPerPage, this.currentPage).subscribe({
        next: (data: any[]) => {
          console.log("Fetched data:", data);
          this.models = [];
          data.flatMap(item => item.get_latest_models).forEach(model => {
            console.log("Model:", model)
              this.models?.push(new Model(
                model.model_id,
                model.model_name,
                model.epochs,
                model.num_frames,
                model.batch_size,
                new Date(model.creation_date),
                model.train,
                model.test,
                model.verification,
                model.shuffle_size,
                model.location_name))
              });
            },
        error: (error) => console.error('Error fetching models:', error)
      });
    }
    catch{
      console.log("No Models Found")
    }
  }

  fetchModelClasses(model: Model, classMap: Map, callback: (classNames: string[]) => void) {
    console.log("Fetching Classes for Selected Model");
    const classNames: string[] = [];
    if(model.model_id) {
      this.getModels.getModelClassesService(model.model_id).subscribe({
        next: (data: any[]) => {
          const classes = data.flatMap(item => item.get_model_classes.classes);
          classes.forEach(class_id => {
            const classString = classMap[class_id];
            if(classString !== undefined) { 
              classNames.push(classString);
            }
          });
          callback(classNames); 
        },
        error: (error) => console.error('Error fetching models:', error)
      });
    }
  }
  
  fetchConfigurationMap(){
    this.mapService.fetchConfigurationMap().subscribe({
      next: (data: any[]) => {
        console.log("Fetched config map:", data);
        this.configMap = [];
        data.flatMap(item => item.get_configuration_map).forEach(config => {
          console.log("Model:", config)
            this.configMap.push(new ModelConfig(
              config.config_id,
              config.config_name,
              config.epochs,
              config.num_frames,
              config.batch_size,
              config.train,
              config.test,
              config.verification,
              config.shuffle_size))
            });
          },
      error: (error) => console.error('Error fetching models:', error)
    });
  }

mapModelConfiguration(model: Model){
  let configName = "Advanced"
  for (const configuration of this.configMap) {
    if (this.findModelMapping(model, configuration)) {
      console.log("Found match:", configuration.config_name);
      configName = configuration.config_name;
      break; 
    }
  }
  return configName;
  }

findModelMapping(model: Model, configuration: ModelConfig) {
  let doesMatch = false;
  if(model.test === configuration.test &&
            model.train === configuration.train &&
            model.epochs === configuration.epochs &&
            model.batch_size === configuration.batch_size &&
            model.num_frames === configuration.num_frames &&
            model.shuffle_size === configuration.shuffle_size &&
            model.verification === configuration.verification){
            doesMatch = true;
            }
  return doesMatch;
  } 

  togglePopup(model: Model) {
    console.log(model)
    this.fetchModelClasses(model, this.classMap!, (classNames) => {
      this.modelInfoClasses = classNames;
    });
    console.log(this.modelInfoClasses)
    this.cdr.detectChanges();
    this.showModelPopup = !this.showModelPopup;
  }
  // Node Functions

  fetchNode() {
    console.log("Fetching Models");
    try{
      this.getNodes.getNodeService(this.itemsPerPage, this.currentPage).subscribe({
        next: (data: any[]) => {
          console.log("Fetched data:", data);
          this.nodes = [];
          data.flatMap(item => item.get_latest_nodes).forEach(node => {
            console.log("Node:", node)
              this.nodes.push(new Node(
              node.node_id,
              node.node_name,
              node.node_address,
              node.status_value,
              new Date(node.creation_date)
                ))
              });
            },
        error: (error) => console.error('Error fetching models:', error)
      });
    }
  catch{
    console.log("No Node Found")
  }
  }

  fetchNodeCount(){
    this.mapService.fetchCountMap().subscribe(countMaps => {
      console.log(countMaps);
      console.log(countMaps[0])
      const countMap = countMaps[0]?.get_count_map;
      if (countMap) {
        console.log("Map:"+countMap);
        console.log("Max Length Map:"+countMap['node_count']);
        this.nodeLength = countMap['node_count'];
        console.log("Max Length Saved:"+this.nodeLength)
        this.cdr.detectChanges();
      } else {
        console.log('Count not retrieved');
      }
    });
  }
  // Device Functions

  fetchDevice(node_id: Node['node_id']) {
    console.log("Fetching Models");
    this.getNodes.getNodeDevices(node_id, this.itemsPerPage, this.currentPage).subscribe({
      next: (data: any[]) => {
        console.log("Fetched data:", data);
        this.devices = [];
        console.log(data[0].get_devices_details.devices)
        data.flatMap(item => item.get_devices_details ? item.get_devices_details.devices : [])
        .forEach(device => {
            console.log("Device:", device);
            this.devices.push(new Device(
                device.device_id,
                device.device_name,
                "Connected",
                new Date(device.creation_date)
            ));
        });
          },
      error: (error) => console.error('Error fetching models:', error)
    });
  }

  // Class Functions

fetchClassMap(){
  this.mapService.fetchClassMap().subscribe(classMaps => {
    this.classMap = classMaps[0]?.get_class_map;
    if (this.classMap) {
      this.cdr.detectChanges();
      }
    else {
      console.log('Class map not retrieved');
    }
  });
}

}
