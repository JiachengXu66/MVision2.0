import { TestBed } from '@angular/core/testing';

import { CreateDeploymentService } from './create-deployment.service';

describe('CreateDeploymentService', () => {
  let service: CreateDeploymentService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CreateDeploymentService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
