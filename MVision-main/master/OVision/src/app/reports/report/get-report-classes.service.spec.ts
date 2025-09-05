import { TestBed } from '@angular/core/testing';

import { GetReportClassesService } from './get-report-classes.service';

describe('GetReportClassesService', () => {
  let service: GetReportClassesService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GetReportClassesService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
