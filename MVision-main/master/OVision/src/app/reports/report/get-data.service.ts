import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Injectable } from '@angular/core';
import { environment } from '../../../shared/environments/environments';
@Injectable({
  providedIn: 'root'
})
export class GetDataService {
  private baseUrl = environment.apiBaseUrl;
  constructor(private http: HttpClient) { }

  getDataService(report_id: string, start_date: Date, end_date: Date, class_ids: any[], deployment_id: number, metric_value: string | null): Observable<any[]> {
    
    const url = `${this.baseUrl}/reports/id/${report_id}/data`;
  
    let classIdsString = JSON.stringify(class_ids);
  
    let params = new HttpParams()
      .set('start_date', start_date.toISOString()) 
      .set('end_date', end_date.toISOString())
      .set('class_ids', classIdsString) 
      .set('deployment_id', deployment_id.toString());
  
    if (metric_value !== null) {
      params = params.set('metric_value', metric_value);
    }
    console.log(params.toString());
    return this.http.get<any[]>(url, { params: params });
  }  
}