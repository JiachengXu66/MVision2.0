import { TestBed } from '@angular/core/testing';

import { GetReportsService } from './get-reports.service';

describe('GetReportsService', () => {
  let service: GetReportsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GetReportsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
