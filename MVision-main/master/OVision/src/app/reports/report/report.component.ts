import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { TimeSet, ConfidenceSet, DataRequest } from 'src/shared/models/DataStructures';
import { Report } from 'src/shared/models/Entities';
import { ActivatedRoute } from '@angular/router';
import { GetGraphService } from './get-graph.service';
import { GetMapService } from '../../passive/get-maps.service';
import { GetReportService } from './get-report.service';
import { GetReportClassesService} from './get-report-classes.service';
import { Observable, firstValueFrom, map } from 'rxjs';

type GraphInfo = {
  graph_type: string;
  value_type: string;
};

type StandardMap = {[key: string]:string}

type Map = { [key: string]: GraphInfo };

type NestedMap = { [key: number]: GraphInfo };
@Component({
  selector: 'app-report',
  templateUrl: './report.component.html',
  styleUrls: ['./report.component.sass']
})
export class ReportComponent implements OnInit {
  private updateIntervalId: any;
  graphMap: Map = {};
  visualise: GraphInfo = {graph_type:'',
  value_type: ''
  };
  classMap: StandardMap = {};

  report: Report | null = null ;
  report_id: number | null = null;
  report_name: string = '';
  range_unit: string = '';

  classes: number[] = [];
  dataSets: ConfidenceSet [] = [];

  chosenDataSet: ConfidenceSet | TimeSet | null = null;

  graphReady: boolean = false;

  currentPage: number = 1;
  itemsPerPage: number = 1;
  pageTitle: string = "";

  constructor(private getGraph: GetGraphService,
              private route: ActivatedRoute,
              private mapService: GetMapService,
              private GetReport: GetReportService,
              private ReportClasses: GetReportClassesService,
              private cdr: ChangeDetectorRef
              ) { }

  ngOnInit() {
    this.fetchClassMaps()
    this.fetchGraphMap();
    this.getGraphType();
    this.fetchReport().then(report =>{
      this.report = report
      this.fetchReportData();
      this.updateIntervalId = setInterval(() => {
        this.fetchReportData();
      }, this.report.frequency_value*this.getFactor(this.report.frequency_unit));
      console.log(this.report.frequency_value*this.getFactor(this.report.frequency_unit))
    }
    ) 
  }

  configureDates(){
    const timeFactor = this.getFactor(this.report!.range_unit)
    const rangeSize = timeFactor * this.report!.range_value
    const end_date = new Date()
    const start_date = new Date(end_date.getTime() - rangeSize);
    return {start_date, end_date}
  }

  async fetchReportData() {
    let newDataSet: ConfidenceSet[]= [];  
    try {
      const classes = await this.fetchReportClasses();
      this.classes = classes;
      const dates = this.configureDates();
  
      const promises = this.classes.map(class_id => this.prepareDataRequest(class_id, dates, newDataSet));
  
      await Promise.all(promises);
      console.log(newDataSet)
      this.dataSets = [...newDataSet];  
      console.log("All data sets fetched and processed.");
    } catch (error) {
      console.error("Error in fetching classes or report data:", error);
    } finally {
      this.cdr.detectChanges();
      this.graphReady = true; 
    }
}

async prepareDataRequest(class_id: number, dates: { start_date: Date, end_date: Date }, newDataSet: ConfidenceSet[]) {
    const request_body = new DataRequest(
      dates.start_date,
      dates.end_date,
      class_id,
      this.report!.deployment_id,
      this.report!.threshold
    );
  
    const data = await firstValueFrom(this.GetReport.getReportData(request_body, this.report!.report_id));
    if (data && data[0] && data[0].get_report_data !== null) {
      const results = data[0].get_report_data[0];
      const dataset = new ConfidenceSet(
        results.classid,
        results.creation_dates,
        results.values
      );
      newDataSet.push(dataset);  
    }
    return true;
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

  fetchReport(): Promise<Report> {
    return firstValueFrom(this.GetReport.getReport(this.report_id!))
      .then(result => {
        const reportData = result[0].get_report[0];
        const report = new Report(
          reportData.report_id,
          reportData.report_name,
          reportData.report_type,
          reportData.deployment_id,
          reportData.frequency_value,
          reportData.frequency_unit,
          new Date(reportData.creation_date),
          reportData.range_value,
          reportData.range_unit,
          reportData.graph_id,
          reportData.threshold
        );
        console.log(report);
        this.report_name = report.report_name
        this.range_unit = report.range_unit
        return report; 
      })
      .catch(error => {
        console.error('Failed to fetch report:', error);
        throw error; 
    })
  }

  fetchGraphMap(){
    this.mapService.fetchGraphMap().subscribe(graphMaps => {
      this.graphMap = graphMaps[0]?.get_graph_map;
    });
    console.log(this.graphMap)
  }

  getGraphType(){
    this.report_id = parseInt(this.route.snapshot.paramMap.get('reportID')!);
    if (this.report_id) {
      this.getGraph.getGraphId(this.report_id).subscribe({
        next: (graph_id) => {
          if (this.graphMap) {
              const graphType = this.graphMap[graph_id[0]?.get_graph_id];
              if (graphType) {
                this.visualise = graphType;
              } 
            } 
            else {
              console.error('Graph map not found in the fetched data.');
            }
          }
          });
    }
  }

  fetchReportClasses(): Promise<any> {
    return firstValueFrom(
      this.ReportClasses.getClasses(this.report!.report_id).pipe(
        map(response => {
          const classes: number[] = response[0]?.get_report_classes?.classes; // Process response
          return classes;
        })
      )
    );
  }
  
  calculateStartDate(frequencyUnit: string, frequencyValue: number) {
    let startDate = new Date();
    switch (frequencyUnit) {
      case 'day':
        startDate.setDate(startDate.getDate() - frequencyValue);
        break;
      case 'week':
        startDate.setDate(startDate.getDate() - (frequencyValue * 7));
        break;
      case 'month':
        startDate.setMonth(startDate.getMonth() - frequencyValue);
        break;
      case 'year':
        startDate.setFullYear(startDate.getFullYear() - frequencyValue);
        break;
      default:
        console.log('Invalid frequency unit:', frequencyUnit);
    }
    return startDate;
  }

  onPageChange(newPage: number) {
    this.currentPage = newPage;
    this.chosenDataSet = this.dataSets[this.currentPage-1];
  }

  fetchClassMaps(){
    this.mapService.fetchClassMap().subscribe(classMaps => {
      this.classMap = classMaps[0]?.get_class_map;
  })
  }

  getClassName(){
      if (this.classMap) {
        const className = this.classMap[this.chosenDataSet!.classid];
        if (className) {
          this.pageTitle ="Activity: "+className.charAt(0).toUpperCase() + className.slice(1);;
        } else {
          this.pageTitle = "Fetch Error"
        }
      }};

  changeTitle(visualise: string) {
    switch(visualise)
    {
      case "line":{
        console.log("line")
        this.getClassName();
        break;
      }
      case "bar":{
        console.log("bar")
        this.pageTitle = "Summary";
        break;
      }
    }
  }
    
}

