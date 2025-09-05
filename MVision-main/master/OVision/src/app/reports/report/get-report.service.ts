import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../shared/environments/environments';
import { DataRequest } from 'src/shared/models/DataStructures';
import { Report } from 'src/shared/models/Entities';
@Injectable({
  providedIn: 'root'
})
export class GetReportService {
  private baseUrl = environment.apiBaseUrl;
  constructor(private http: HttpClient) { }

  getReport(report_id: number): Observable<any[]> {

    const url = `${this.baseUrl}/reports/id/${report_id}`;

    return this.http.get<any[]>(url);
  }

  getReportData(request: DataRequest, report_id: Report['report_id']): Observable<any[]> {
    
    const url = `${this.baseUrl}/reports/id/${report_id}/data`;
  
    let params = new HttpParams()
      .set('start_date', request.start_date.toISOString())
      .set('end_date', request.end_date.toISOString())
      .set('class_id', request.class_id)
      .set('deployment_id', request.deployment_id)
      .set('threshold', request.threshold);

    console.log(params.toString());
    return this.http.get<any[]>(url, { params: params });
  }  
}
