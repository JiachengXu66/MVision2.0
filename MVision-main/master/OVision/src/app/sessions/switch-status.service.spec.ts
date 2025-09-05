import { TestBed } from '@angular/core/testing';

import { SwitchStatusService } from './switch-status.service';

describe('SwitchStatusService', () => {
  let service: SwitchStatusService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SwitchStatusService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
