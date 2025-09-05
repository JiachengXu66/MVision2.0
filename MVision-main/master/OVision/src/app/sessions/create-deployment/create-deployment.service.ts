import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {Deployment } from '../../../shared/models/Entities'
import { environment } from '../../../shared/environments/environments';

@Injectable({
  providedIn: 'root'
})
export class CreateDeploymentService {
  private baseUrl = environment.apiBaseUrl;
  constructor(private http: HttpClient) { }

  postDeployment(deployment: Deployment) {
    const url = `${this.baseUrl}/deployments/create`;
    return this.http.post(url, deployment);
  }
}