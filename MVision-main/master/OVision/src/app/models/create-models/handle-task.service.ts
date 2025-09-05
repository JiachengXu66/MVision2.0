import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ModelConfig, Task } from 'src/shared/models/Entities';
import { environment } from '../../../shared/environments/environments';
@Injectable({
  providedIn: 'root'
})
export class HandleTaskService {
  private baseUrl = environment.apiBaseUrl;
  constructor(private http: HttpClient) { }


  fetchTask(task_id: number): Observable<any[]> {
    const url = `${this.baseUrl}/tasks/id/${task_id}`;

    return this.http.get<any[]>(url);
  }

  submitTask(modelName: string, selectedConfig: ModelConfig, classes: number[]): Observable<{ task_id: [{ insert_model_task: number }] }> {
    const url = `${this.baseUrl}/tasks/create`;
    const task = new Task(
      9999,
      modelName,
      new Date(),
      'queue',
      classes,
      [3],
      selectedConfig.epochs,
      selectedConfig.num_frames,
      selectedConfig.batch_size,
      selectedConfig.train,
      selectedConfig.test,
      selectedConfig.verification,
      selectedConfig.shuffle_size
    );
    console.log("Submitting Task:");
    console.log(task);
    return this.http.post<{ task_id: [{ insert_model_task: number }] }>(url, task);
  }
}
