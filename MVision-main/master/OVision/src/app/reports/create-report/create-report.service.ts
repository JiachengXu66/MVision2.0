import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ReportConfig } from '../../../shared/models/Entities'
import { environment } from '../../../shared/environments/environments';
@Injectable({
  providedIn: 'root'
})
export class CreateReportService {

  private baseUrl = environment.apiBaseUrl;
  constructor(private http: HttpClient) { }


  postReport(report: ReportConfig) {
    const url = `${this.baseUrl}/reports/create`;
    return this.http.post(url, report);
  }
}
