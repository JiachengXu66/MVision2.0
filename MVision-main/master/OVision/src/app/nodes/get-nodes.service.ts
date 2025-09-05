import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../shared/environments/environments';
@Injectable({
  providedIn: 'root'
})
export class GetNodesService {
  
  constructor(private http: HttpClient) { }

  private baseUrl = environment.apiBaseUrl;
  getNodeService(itemLimit: number = 10, currentPage: number = 1): Observable<any[]> {

    const model_url = `${this.baseUrl}/nodes/`;

    const params = new HttpParams()
      .set('itemLimit', itemLimit.toString())
      .set('currentPage', currentPage.toString());

    return this.http.get<any[]>(model_url, { params });
  }

  getNodeDevices(node_id: number, itemLimit: number = 10, currentPage: number = 1): Observable<any[]> {

    const model_url = `${this.baseUrl}/nodes/id/${node_id}/devices/connected`;
    
    const params = new HttpParams()
      .set('itemLimit', itemLimit.toString())
      .set('currentPage', currentPage.toString());
    return this.http.get<any[]>(model_url, {params});
  }
}