import { TestBed } from '@angular/core/testing';

import { HandleTaskService } from './handle-task.service';

describe('HandleTaskService', () => {
  let service: HandleTaskService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(HandleTaskService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
