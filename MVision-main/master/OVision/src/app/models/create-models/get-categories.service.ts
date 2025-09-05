import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../shared/environments/environments';
@Injectable({
  providedIn: 'root'
})
export class GetCategoriesService {
  private baseUrl = environment.apiBaseUrl;
  constructor(private http: HttpClient) { }


  getCategories(): Observable<any[]> {

    const url = `${this.baseUrl}/models/categories/`;

    return this.http.get<any[]>(url);
  }
}
