import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { GetModelService } from './get-models.service';
import { GetMapService } from '../passive/get-maps.service';
import { Model, ModelConfig } from 'src/shared/models/Entities';
import { config } from 'rxjs';

@Component({
  selector: 'app-targets',
  templateUrl: './models.component.html',
  styleUrls: ['./models.component.sass']
})
export class ModelsComponent implements OnInit {
  models: Model[] = [];
  currentPage: number = 1;
  itemsPerPage: number = 4;
  maxLength: number = 1;
  configMap: ModelConfig[] = [];
  constructor(private cdr: ChangeDetectorRef,
    private getModels: GetModelService,
    private mapService: GetMapService) { }

  ngOnInit() {
    console.log("Updating pages")
    this.fetchModelCount();
    this.fetchModel();
    this.fetchConfigurationMap();
  } 

  onPageChange(newPage: number) {
    this.currentPage = newPage;
    console.log(this.currentPage)
    this.fetchModel();
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

  fetchModelCount(){
    this.mapService.fetchCountMap().subscribe(countMaps => {
      console.log(countMaps);
      console.log(countMaps[0])
      const countMap = countMaps[0]?.get_count_map;
      if (countMap) {
        console.log("Map:"+countMap);
        console.log("Max Length Map:"+countMap['model_count']);
        this.maxLength = countMap['model_count'];
        console.log("Max Length Saved:"+this.maxLength)
        this.cdr.detectChanges();
      } else {
        console.log('Count not retrieved');
      }
    });
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
    console.log("Mapping Model", model.model_name)
    for (const configuration of this.configMap) {
      if (this.findModelMapping(model, configuration)) {
        console.log("Found match:", configuration.config_name);
        configName = configuration.config_name;
        break; 
      }
    }
    return configName;
  }

  fetchModel() {
    console.log("Fetching Models");
    this.getModels.getModelService(this.itemsPerPage, this.currentPage).subscribe({
      next: (data: any[]) => {
        console.log("Fetched data:", data);
        this.models = [];
        data.flatMap(item => item.get_latest_models).forEach(model => {
          console.log("Model:", model)
            this.models.push(new Model(
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

}
