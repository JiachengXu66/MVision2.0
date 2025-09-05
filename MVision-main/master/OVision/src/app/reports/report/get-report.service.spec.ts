import { TestBed } from '@angular/core/testing';

import { GetReportService } from './get-report.service';

describe('GetReportService', () => {
  let service: GetReportService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GetReportService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
