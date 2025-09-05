import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../shared/environments/environments';
@Injectable({
  providedIn: 'root'
})
export class GetReportClassesService {
  private baseUrl = environment.apiBaseUrl;
  constructor(private http: HttpClient) { }


  getClasses(report_id: number): Observable<any[]> {

    const url = `${this.baseUrl}/reports/id/${report_id}/classes`;

    return this.http.get<any[]>(url);
  }
}
