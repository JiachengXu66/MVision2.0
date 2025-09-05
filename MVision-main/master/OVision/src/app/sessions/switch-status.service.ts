import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Deployment } from '../../shared/models/Entities'
import { environment } from '../../shared/environments/environments';
@Injectable({
  providedIn: 'root'
})
export class SwitchStatusService {
  private baseUrl = environment.apiBaseUrl;
  constructor(private http: HttpClient) { }

  switchStatus(deployment: Deployment) {
    const url = `${this.baseUrl}/deployments/switch/status`;
    return this.http.post(url, deployment);
  }
}