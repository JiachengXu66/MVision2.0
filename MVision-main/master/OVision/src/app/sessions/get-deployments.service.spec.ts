import { TestBed } from '@angular/core/testing';

import { GetDeploymentsService } from './get-deployments.service';

describe('GetDeploymentsService', () => {
  let service: GetDeploymentsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GetDeploymentsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
