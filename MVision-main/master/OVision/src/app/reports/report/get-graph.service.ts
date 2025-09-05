import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../shared/environments/environments';
@Injectable({
  providedIn: 'root'
})
export class GetGraphService {
  private baseUrl = environment.apiBaseUrl;
  constructor(private http: HttpClient) { }


  getGraphId(_report_id: number): Observable<any[]> {

    const url = `${this.baseUrl}/reports/id/${_report_id}/graph`;

    return this.http.get<any[]>(url);
  }
}
