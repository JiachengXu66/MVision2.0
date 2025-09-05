import { ChangeDetectionStrategy, ChangeDetectorRef, Component } from '@angular/core';
import { ModelConfig, Task } from '../../../shared/models/Entities'
import { GetMapService } from '../../passive/get-maps.service';
import { GetCategoriesService } from './get-categories.service';
import { HandleTaskService } from './handle-task.service';

type Map = { [key: string]: string };

@Component({
  selector: 'app-create-models',
  templateUrl: './create-models.component.html',
  styleUrls: ['./create-models.component.sass'],
  changeDetection: ChangeDetectionStrategy.OnPush
})

export class CreateModelsComponent { 

  modelName: string = '';

  advancedSettings: boolean = false;
  phase1: boolean = true;
  nextButtonStatus: boolean = true;
  previousButtonStatus: boolean = true;

  configMap: ModelConfig[] = [];
  selectedConfig: ModelConfig | null = null;
  availableConfig: ModelConfig[] = [];
  
  classMap: Map | null = null;
  categoryMap: Map | null = null;

  categorisedClasses: any[] = [];
  categorisedClassesString: Map | null = null;
  categories: string[] = [];
  categoriesExpanded: boolean[] = [];

  customEpochs: number = 0;
  customNumFrames: number = 0;
  customBatchSize: number = 0;
  customTrain: number = 0;
  customTest: number = 0;
  customVerification: number = 0;
  customShuffleSize: number = 0;

  chosenClasses: any[] = [];
  taskRunning: boolean = false;
  taskId: number | null = null;
  submittedTask: Task | null = null;

  constructor(private cdr: ChangeDetectorRef,
    private mapService: GetMapService,
    private categoriesService: GetCategoriesService,
    private taskService: HandleTaskService
    ) { }

    ngOnInit() {
      console.log("Updating pages")
      this.fetchClassMap();
      this.fetchConfigurationMap();
      this.fetchCategoryMap();
    } 

    onConfigChange(){
      if(this.selectedConfig){
      this.customEpochs = this.selectedConfig.epochs;
      this.customNumFrames = this.selectedConfig.num_frames;
      this.customBatchSize = this.selectedConfig.batch_size;
      this.customTrain = this.selectedConfig.train;
      this.customTest = this.selectedConfig.test;
      this.customVerification = this.selectedConfig.verification;
      this.customShuffleSize = this.selectedConfig.shuffle_size;
    };
    if(this.selectedConfig && this.modelName.trim())
    {
      this.nextButtonStatus = false;
    }
    else
    {
      this.nextButtonStatus = true;
    }
  };

    fetchCategoryMap(){
        this.mapService.fetchCategoryMap().subscribe(categoryMaps => {
          this.categoryMap = categoryMaps[0]?.get_categories_map;
          if (this.categoryMap) {
            this.cdr.detectChanges();
          } else {
            console.log('Category map not retrieved');
          }
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

    fetchConfigurationMap(){
      this.mapService.fetchConfigurationMap().subscribe({
        next: (data: any[]) => {
          this.configMap = [];
          data.flatMap(item => item.get_configuration_map).forEach(config => {
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
    };
    
    fetchTask() {
      if (this.taskId) {
        this.taskService.fetchTask(this.taskId).subscribe(taskResponse => {
          console.log(taskResponse);
          const taskObj = taskResponse[0].get_task[0];
          console.log(taskObj);
          if (taskObj) {
            this.submittedTask = new Task(
              taskObj.task_id,
              taskObj.model_name,
              new Date(taskObj.creation_date), 
              taskObj.status_value,
              [], 
              [], 
              taskObj.epochs,
              taskObj.num_frames,
              taskObj.batch_size,
              taskObj.train,
              taskObj.test,
              taskObj.verification,
              taskObj.shuffle_size
            );
          }
          this.taskRunning = true;
          this.cdr.detectChanges();
        });
      }
    }

    checkTaskStatus() {
      console.log(this.submittedTask?.status_value)
      if (!(this.submittedTask?.status_value === 'failed' || this.submittedTask?.status_value === 'trained') && this.taskId) {// Fetch the task status
        this.fetchTask();
        setTimeout(() => {
          this.checkTaskStatus();
        }, 1000);
      } else {
        console.log("Task completed or condition not met, stopping polling.");
      }
    }

    organiseClasses(){
      this.categoriesService.getCategories().subscribe(categorisedClasses => {
        this.categorisedClasses = categorisedClasses[0]?.get_categorised_classes;
        if (this.categorisedClasses && this.categoryMap && this.classMap) {
          this.categorisedClassesString = this.convertToText(this.categorisedClasses, this.categoryMap, this.classMap);
          if(this.categorisedClassesString){
            this.categories = Object.keys(this.categorisedClassesString);
            this.categoriesExpanded = this.categories.map(() => false);
          }
          this.cdr.detectChanges();
        } else {
        }
      });
    }

    selectValues(category: string){
      if(this.categorisedClassesString){
        return this.categorisedClassesString[category]
      }
      else{
        return
      }
    }

    updateSelection(){
      if (this.selectedConfig) {
        this.selectedConfig = null;
      }
      this.selectedConfig = new ModelConfig(0,
                            'Custom',
                            this.customEpochs,
                            this.customNumFrames,
                            this.customBatchSize,
                            this.customTrain,
                            this.customTest,
                            this.customVerification,
                            this.customShuffleSize);
      this.nextButtonStatus = false;
    };

    getClasses(){
      this.phase1 = false;
      this.advancedSettings = false;
      this.previousButtonStatus = false;
      this.organiseClasses();
    };

    convertToText(originalJson: any, categoriesMap: Map, classesMap: Map): any {
      const remapped = Object.keys(originalJson).reduce((acc: any, key) => {
        const category = categoriesMap[key];
        const classIds = originalJson[key];
        const classTexts = classIds.map((classId: string) => classesMap[classId.toString()]);
        acc[category] = classTexts;
        return acc;
      }, {});
  
      return remapped;
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

    isChecked(className: string): boolean {
      const check_result = this.chosenClasses.includes(className)
      console.log(`${className}: is ${check_result}`)
      return check_result;
    }

    toggleClassSelection(className: string, isChecked: boolean): void {
      if (!isChecked) {
        if (!this.chosenClasses.includes(className)) {
          this.chosenClasses.push(className);
        }
      } else {        
        this.chosenClasses = this.chosenClasses.filter(c => c !== className);
      }
    }

    returnToModelConfig()
    {
      this.phase1 = true;
      this.advancedSettings = false;
      this.previousButtonStatus = true;
    }

    submitTask() {
      const classes = this.convertToID();
      if (this.selectedConfig && this.modelName && classes) {
        this.taskService.submitTask(this.modelName, this.selectedConfig, classes).subscribe({
          next: (response) => {
            console.log(response)
            this.taskId = response.task_id[0].insert_model_task;
            console.log(this.taskId)
            console.log("Fetching Task")
            this.fetchTask();
            this.checkTaskStatus();
          },
          error: (error) => console.error('Error:', error),
        });
      }
    }; 
    
}
