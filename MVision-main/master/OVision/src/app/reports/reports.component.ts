import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { GetReportsService } from './get-reports.service';
import { GetMapService } from '../passive/get-maps.service';
import { Report } from 'src/shared/models/Entities';

@Component({
  selector: 'app-reports',
  templateUrl: './reports.component.html',
  styleUrls: ['./reports.component.sass']
})
export class ReportsComponent implements OnInit {
  reports: Report[] = [];
  currentPage: number = 1;
  itemsPerPage: number = 8;
  maxLength: number = 1;

  constructor(private cdr: ChangeDetectorRef,
    private getReportsService: GetReportsService,
    private mapService: GetMapService) { }

  ngOnInit() {
      console.log("Updating pages")
      this.fetchReportCount();
      this.fetchReports();
    } 
  
  onPageChange(newPage: number) {
      this.currentPage = newPage;
      console.log(this.currentPage)
      this.fetchReports();
    }

  fetchReportCount(){
    this.mapService.fetchCountMap().subscribe(countMaps => {
      console.log(countMaps);
      console.log(countMaps[0])
      const countMap = countMaps[0]?.get_count_map;
      if (countMap) {
        console.log(countMap);
        console.log(countMap['report_count']);
        this.maxLength = countMap['report_count'];
        console.log(this.maxLength)
        this.cdr.detectChanges();
      } else {
        console.log('Count not retrieved');
      }
    });
  }
  
  fetchReports() {
    this.getReportsService.getReports(this.itemsPerPage, this.currentPage).subscribe({
      next: (data: any[]) => {
        const reports = data.flatMap(item => item.get_latest_reports).map(report => new Report(
          report.report_id,
          report.report_name,
          report.report_type,
          report.deployment_id,
          report.frequency_value,
          report.frequency_unit,
          new Date(report.creation_date), 
          report.range_value,
          report.range_unit,
          report.graph_id,
          report.threshold
        ));
        this.reports = reports;
      },
      error: (error) => console.error('Error fetching deployments:', error)
    });
  }
}
