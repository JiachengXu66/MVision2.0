import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from '../../shared/environments/environments';
import { Deployment } from 'src/shared/models/Entities';
@Injectable({
  providedIn: 'root'
})
export class GetDeploymentsService {
  private baseUrl = environment.apiBaseUrl;
  constructor(private http: HttpClient) { }


  getDeployments(itemLimit: number = 10, currentPage: number = 1): Observable<any[]> {

    const url = `${this.baseUrl}/deployments`;

    const params = new HttpParams()
      .set('itemLimit', itemLimit.toString())
      .set('currentPage', currentPage.toString());

    return this.http.get<any[]>(url, { params });
  }

  getDeployment(deployment_id: Deployment['deployment_id']): Observable<any[]> {

    const url = `${this.baseUrl}/deployments/id${deployment_id}`;
    return this.http.get<any[]>(url);
    }
}
