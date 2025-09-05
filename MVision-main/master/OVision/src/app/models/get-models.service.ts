import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Model } from '../../shared/models/Entities'
import { environment } from '../../shared/environments/environments';
@Injectable({
  providedIn: 'root'
})
export class GetModelService {
  private baseUrl = environment.apiBaseUrl;
  constructor(private http: HttpClient) { }

  getModelService(itemLimit: number = 10, currentPage: number = 1): Observable<any[]> {

    const model_url = `${this.baseUrl}/models/`;

    const params = new HttpParams()
      .set('itemLimit', itemLimit.toString())
      .set('currentPage', currentPage.toString());

    return this.http.get<any[]>(model_url, { params });
  }

  getModelClassesService(model_id: Model['model_id']): Observable<any[]>{
    const url = `${this.baseUrl}/models/id/${model_id}/classes`;

    return this.http.get<any[]>(url);
  }
}
