import { TestBed } from '@angular/core/testing';

import { GetTargetService } from './get-targets.service';

describe('GetTargetsService', () => {
  let service: GetTargetService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GetTargetService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
