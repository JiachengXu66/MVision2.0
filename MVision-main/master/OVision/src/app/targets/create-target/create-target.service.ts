import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Person, Location } from '../../../shared/models/Entities'
import { environment } from '../../../shared/environments/environments';
@Injectable({
  providedIn: 'root'
})
export class CreateTargetService {
  private baseUrl = environment.apiBaseUrl;
  constructor(private http: HttpClient) { }


  postPerson(person: Person) {
    const url = `${this.baseUrl}/targets/create`;
    return this.http.post(url, person);
  }

  postLocation(location: Location) {
    const url = `${this.baseUrl}/targets/create`;
    return this.http.post(url, location);
  }
}