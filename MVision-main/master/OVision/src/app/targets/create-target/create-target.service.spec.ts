import { TestBed } from '@angular/core/testing';

import { CreateTargetService } from './create-target.service';

describe('CreateTargetService', () => {
  let service: CreateTargetService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CreateTargetService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
