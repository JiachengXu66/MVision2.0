import { ChangeDetectorRef, Component } from '@angular/core';
import { Router } from '@angular/router';

import { GetDeploymentsService } from '../../sessions/get-deployments.service';
import { GetMapService } from '../../passive/get-maps.service';
import { GetModelService } from '../../models/get-models.service';
import { CreateReportService } from './create-report.service';

import { Deployment, ReportConfig, Model } from 'src/shared/models/Entities';
import { CountSet, TimeSet, ConfidenceSet } from 'src/shared/models/DataStructures';
type Map = { [key: string]: string };
type NestedMap = { [key: string]: { [key: string]: string } };
@Component({
  selector: 'app-create-report',
  templateUrl: './create-report.component.html',
  styleUrls: ['./create-report.component.sass']
})
export class CreateReportComponent {
  selectedReportType: string = 'Count Detections';
  selectedGraphType: string = 'line';

  typeMap: Map = {'Count Detections':'Count','Time Spent':'Time','Confidence Map':'Confidence'}

  displayOptionsConfig: boolean = true;
  displayOptionsDeployment: boolean = false;
  displayOptionsClasses: boolean = false;

  updateFrequency: number = 1;
  historyRange: number = 20;
  selectedFrequency: string = 'minute'
  selectedRange: string = 'minute'
  confidenceThreshold: number = 50;
  selectedValueType: string = 'total'

  deploymentSessions: Deployment[] = [];
  selectedDeployment: Deployment | null = null;
  reportName: string = '';

  modelInfoClasses: string[] = []
  classButtonStatus: boolean = true;
  classMap: Map | null = null;

  chosenClasses: any[] = [];
  classIds:any[] = [];
  
  currentPage: number = 1;
  itemsPerPage: number = 4;
  maxLength: number = 1;

  submitButtonStatus: boolean = true;

  chosenDataSet: ConfidenceSet[] | CountSet[] | TimeSet[] | null = null;
  tempCountSet: CountSet[] = [];
  tempConfidenceSet: CountSet[] = [];
  tempTimeSet: TimeSet[] = [];

  graphMap: NestedMap = {};
   
  constructor(private router: Router,
    private getDeploymentsService: GetDeploymentsService,
    private mapService: GetMapService,
    private cdr: ChangeDetectorRef,
    private getModels: GetModelService,
    private postReport: CreateReportService) { }
  
  selectConfig(){
    this.displayOptionsClasses = false;
    this.displayOptionsDeployment = false;

    this.displayOptionsConfig = true;
  }

  selectDeployment(){
    this.displayOptionsConfig = false;
    this.displayOptionsClasses = false;

    this.displayOptionsDeployment = true;
  }

  selectClasses(){
    this.displayOptionsConfig = false;
    this.displayOptionsDeployment = false;

    this.fetchModelClasses(this.selectedDeployment!.model_id, this.classMap!, (classNames) => {
      this.modelInfoClasses = classNames;
    });
    this.displayOptionsClasses = true;
  }

  fetchModelClasses(model_id: Model['model_id'], classMap: Map, callback: (classNames: string[]) => void) {
    const classNames: string[] = [];
    if(model_id) {
      this.getModels.getModelClassesService(model_id).subscribe({
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

  ngOnInit() {
    console.log("Updating pages")
    this.fetchDeploymentCount();
    this.fetchDeployments();
    this.fetchClassMap();
    this.fetchGraphMap();
  } 

  onPageChange(newPage: number) {
    this.currentPage = newPage;
    this.fetchDeployments();
  }

  updateDeploymentSelection(deployment: Deployment){
      this.selectedDeployment = deployment;
      this.classButtonStatus = false;
      this.chosenClasses = [];
      this.submitButtonStatus = true;
      this.configureGraph();
  }

  submitReport(){
    const graphId = this.findGraphId()
    console.log(graphId)
    console.log(this.reportName)
    if(graphId && this.reportName.trim()){
    const finalReport = new ReportConfig(
        9999,
        this.reportName,
        this.typeMap[this.selectedReportType],
        this.selectedDeployment!.deployment_id,
        this.updateFrequency,
        this.selectedFrequency,
        new Date(),
        this.historyRange,
        this.selectedRange,
        parseInt(graphId),
        this.confidenceThreshold,
        this.classIds)
        console.log(finalReport)
        this.postReport.postReport(finalReport).subscribe({
          next: (response) => console.log(response),
          error: (error) => console.error('Error:', error),
        });
        this.cdr.detectChanges();
        this.changeToView();
    }
  }

  findGraphId(): string | null {
    for (const id in this.graphMap) {
      console.log(id)
      if (this.graphMap.hasOwnProperty(id)) {
        const info = this.graphMap[id];
        if (info['graph_type'] === this.selectedGraphType && info['value_type'] === this.selectedValueType) {
          return id;
        }
      }
    }
    return null; 
  }
  
  fetchDeploymentCount(){
    this.mapService.fetchCountMap().subscribe(countMaps => {
      const countMap = countMaps[0]?.get_count_map;
      if (countMap) {
        this.maxLength = countMap['deployment_count'];
        this.cdr.detectChanges();
      } else {
        console.log('Count not retrieved');
      }
    });
  }

  fetchGraphMap(){
    this.mapService.fetchGraphMap().subscribe(graphMaps => {
      this.graphMap = graphMaps[0]?.get_graph_map;
    });
    console.log(this.graphMap)
  }

  fetchDeployments() {
    console.log("Fetching deployments")
    this.getDeploymentsService.getDeployments(this.itemsPerPage, this.currentPage).subscribe({
      next: (data: any[]) => {
        this.deploymentSessions = [];
        console.log("Fetched data:", data);
        const deployments = data.flatMap(item => item.get_latest_deployments).map(deployment => {
          return new Deployment(
            deployment.deployment_id, 
            deployment.deployment_name,
            deployment.target_id,
            deployment.status_value,
            deployment.model_id,
            new Date(deployment.creation_date), 
            new Date(deployment.start_date),
            new Date(deployment.expiry_date),
            deployment.node_id,
            deployment.device_id
          );
        });
        this.deploymentSessions = deployments;
      },
      error: (error) => console.error('Error fetching deployments:', error)
    });
  }

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

  changeToView(){
    this.router.navigate(['/reports/view'])
  }

  toggleClassSelection(className: string, isChecked: boolean): void {
    if (!isChecked) {
      if (!this.chosenClasses.includes(className)) {
        this.chosenClasses.push(className);
      }
    } else {        
      this.chosenClasses = this.chosenClasses.filter(c => c !== className);
    }
    this.configureGraph()
    this.submitButtonStatus = false
  }

  isChecked(className: string): boolean {
    const check_result = this.chosenClasses.includes(className)
    return check_result;
  }

  configureGraph() {
    const rangeFactor = this.getFactor(this.selectedRange);
    const frequencyFactor = this.getFactor(this.selectedFrequency);
    const currentTime = new Date();
    const startTime = new Date(currentTime.getTime() - (this.historyRange) * rangeFactor);
    console.log("Configuring Graph")
    let time = new Date(startTime);
    this.tempCountSet = [];
    this.tempTimeSet = [];
    this.tempConfidenceSet = [];
    if (this.chosenClasses.length > 0){
      console.log("Classes Populated")
      const Ids = this.convertToID()
      if(Ids){
        this.classIds = Ids
      }
      Ids?.forEach(classId =>{
        const results = this.generateDatasets(frequencyFactor, currentTime, time)
        if (this.selectedReportType === 'Count Detections') {
              this.tempCountSet.push(new CountSet(classId, results.dateValues, results.values));
        } else if (this.selectedReportType === 'Time Spent') {
            this.tempTimeSet.push(new TimeSet(classId, results.dateValues, results.values, "hours"));
        }
        else if (this.selectedReportType === 'Confidence Map') {
          this.tempConfidenceSet.push(new ConfidenceSet(classId, results.dateValues, results.values));     
        }
        

      })
    if(!(this.tempCountSet.length === 0))
      {
        this.chosenDataSet = this.tempCountSet
      }
    else if(!(this.tempTimeSet.length === 0))
    {
      this.chosenDataSet = this.tempTimeSet
    }
    else if (!(this.tempConfidenceSet.length === 0))
      {
        this.chosenDataSet = this.tempConfidenceSet
      }
    }
    else{
      console.log("No Classes Chosen Temporary Data Shown")
      const results = this.generateDatasets(frequencyFactor, currentTime, time)
      console.log("Data retrieved",results)
      if (this.selectedReportType === 'Count Detections') {
        this.chosenDataSet = [new CountSet(1, results.dateValues, results.values)]
      }
      else if (this.selectedReportType === 'Time Spent'){
        this.chosenDataSet = [new TimeSet(1, results.dateValues, results.values, "hours")]
      }
      else if (this.selectedReportType === 'Confidence Map') {
        this.chosenDataSet = [new ConfidenceSet(1, results.dateValues, results.values)]
      }
    }
    console.log(this.chosenDataSet)
}


generateDatasets(frequencyFactor: number, currentTime: Date, time: Date){
  let dateValues: string[] = [];
  let values: number[] = [];

  while (time.getTime() < currentTime.getTime()) {
      time = new Date(time.getTime() + this.updateFrequency * frequencyFactor);
      if (time > currentTime) {
          break;
      }
      dateValues.push(time.toISOString().replace('Z', '').replace('T', ' '));

      if(this.selectedValueType == "total" && this.selectedReportType == "Count Detections"){
        values.push(Math.round(Math.random())); 
      }
      else{
        values.push(Math.floor(Math.random() * 100)); 
      }
    
  }
  return {dateValues, values};
}

  getFactor(selectedItem: string){
    let factor;
  switch (selectedItem) {
    case 'second':
      factor = 1000; 
      break;
    case 'minute':
      factor = 60000; 
      break
    case 'hour':
      factor = 3600000; 
      break;
    case 'day':
      factor = 86400000; 
      break;
    case 'week':
      factor = 604800000; 
      break;
    case 'month':
      factor = 2629800000; 
      break;
    case 'year':
      factor = 31557600000; 
      break;
    default:
      factor = 0; 
      }
    return factor;
    }

    convertToID() {
      if (!this.classMap) {
        console.error('classMap is null');
        return;
      }
      const invertedClassMap = Object.entries(this.classMap).reduce((acc: {[key: string]: number}, [key, value]) => {
        acc[value] = Number(key);
        return acc;
      }, {});
      return this.chosenClasses.map(className => invertedClassMap[className] ?? null);
    }
}
